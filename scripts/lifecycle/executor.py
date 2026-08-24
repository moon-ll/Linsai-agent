#!/usr/bin/env python3
"""生命周期 cron 框架单步执行器。"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import file_lock, now_utc

from .constants import (
    IDEA_REVIEW_THRESHOLD,
    JOB_STATUS_DONE,
    JOB_STATUS_FAILED,
    JOB_STATUS_PENDING,
    JOB_STATUS_RUNNING,
    MAX_IDEA_REVIEW_ATTEMPTS,
    STALE_RUNNING_SECONDS,
    STEP_CRITIC,
    STEP_GAP_IDENTIFY,
    STEP_IDEA_REVIEW,
    STEP_LIT_NOTE,
    STEP_LIT_READ,
    STEP_LIT_SEARCH,
    STEP_MONITOR,
    STEP_RESEARCHER,
    STEP_UPDATE_METHOD_MANUAL,
    STEP_UPDATE_VISION,
    STEP_WRITER,
    critic_writer_timeout_s,
)
from .utils import _is_stale, _make_job_id

try:
    from adversarial_governance import AdversarialGovernance
except Exception:
    AdversarialGovernance = None  # type: ignore[misc,assignment]

try:
    from llm_router import router as llm_router
except Exception:
    llm_router = None  # type: ignore[misc,assignment]

try:
    from logger import get_logger
    _log = get_logger("lifecycle_cron")
except Exception:
    _log = None


def pick_next_job(self, proposal_id: str) -> Optional[Dict[str, Any]]:
    """挑选下一个可执行的 pending job（同一 proposal 串行）。"""
    prop_state = self._get_proposal_state(proposal_id)
    if not prop_state or prop_state.get("status") != "optimizing":
        return None

    jobs = self._get_jobs(proposal_id)
    if not jobs:
        return None

    # 若有 running 任务，先检查是否 stale
    for job in jobs:
        if job.get("status") == JOB_STATUS_RUNNING and _is_stale(job):
            if _log:
                _log.warning(f"[{proposal_id}] job {job['job_id']} 运行超 {STALE_RUNNING_SECONDS}s，标记失败")
            job["status"] = JOB_STATUS_FAILED
            job["finished_at"] = now_utc()
            job["last_error"] = "运行超时/进程僵死"
            job["attempts"] = job.get("attempts", 0) + 1
            self._save_jobs(proposal_id, jobs)
            break  # 只处理一个 stale，让下次调用继续

    # 重新加载，找第一个依赖满足且 pending 的 job
    jobs = self._get_jobs(proposal_id)
    done_ids = {j["job_id"] for j in jobs if j.get("status") == JOB_STATUS_DONE}
    running = [j for j in jobs if j.get("status") == JOB_STATUS_RUNNING]
    if running:
        return None  # 串行：有任务在跑就等待

    for job in jobs:
        if job.get("status") != JOB_STATUS_PENDING:
            continue
        deps = job.get("depends_on", [])
        if all(d in done_ids for d in deps):
            return job
    return None

def _mark_degradation(self, proposal_id: str, step: str, detail: str) -> None:
    """v6.8.3: 记录降级事件到 proposal_state（质量可追溯）。"""
    try:
        prop_state = self._get_proposal_state(proposal_id)
        if not prop_state:
            return
        degradations = prop_state.get("degradation_events", [])
        degradations.append({"step": step, "detail": detail, "at": now_utc()})
        # 只保留最近 20 条
        prop_state["degradation_events"] = degradations[-20:]
        self._set_proposal_state(proposal_id, prop_state)
    except Exception:
        pass  # 非关键路径，不影响主流程

def _update_job(self, proposal_id: str, job: Dict[str, Any], status: str, error: str = "") -> None:
    jobs = self._get_jobs(proposal_id)
    existing = self._job_by_id(jobs, job["job_id"])
    if not existing:
        return
    existing["status"] = status
    existing["finished_at"] = now_utc() if status in (JOB_STATUS_DONE, JOB_STATUS_FAILED) else ""
    if status == JOB_STATUS_RUNNING:
        existing["started_at"] = now_utc()
    if error:
        existing["last_error"] = error[:500]
    if status == JOB_STATUS_DONE:
        # v6.8.27: 成功时清空 last_error，避免历史错误误导看板
        existing["last_error"] = ""
    if status == JOB_STATUS_FAILED:
        existing["attempts"] = existing.get("attempts", 0) + 1
    self._save_jobs(proposal_id, jobs)

def _read_critic_report(self, prop_dir: Path, round_num: int) -> Dict[str, Any]:
    """读取指定轮次的 critic 报告并解析分数。"""
    report_path = prop_dir / "05_review" / f"critic-round-{round_num}.md"
    if not report_path.exists():
        return {"output": "", "score": 0.0, "dim_scores": {}, "issues": []}
    text = report_path.read_text(encoding="utf-8")
    file_result = {"output": text}
    return {
        "output": text,
        "score": self._extract_score(file_result),
        "dim_scores": self._extract_dimension_scores(file_result, min_output_len=300),
        "issues": self._extract_issues(file_result),
    }

def _run_critic_step(self, proposal_id: str, job: Dict[str, Any]) -> Dict[str, Any]:
    """执行 critic 步骤，并在需要时插入 researcher job。"""
    prop_dir = self._find_proposal_dir(proposal_id)
    if not prop_dir:
        return {"success": False, "error": "proposal 目录不存在"}

    prop_state = self._get_proposal_state(proposal_id)
    project_type = prop_state.get("project_type", "general")
    round_num = job["round"]
    section_key = job.get("section_key", "rationale")
    from proposal_sections import PROPOSAL_SECTIONS, ProposalSections
    section = next((s for s in PROPOSAL_SECTIONS if s["key"] == section_key), None)
    focus_section = section
    is_full_review = section_key == "full_review"

    # v6.9.30: 程序化 AI 写作模式检测——critic 之前运行，产出表达质量天花板
    # （与 optimize.py 的 _run_optimization_round 对齐；微调度器路径此前完全缺失）
    sections_obj = ProposalSections(prop_dir / "04_proposal")
    sections_obj.ensure_split()
    ai_check = self._detect_ai_patterns(prop_dir, sections_obj)
    if _log:
        _log.info(f"[{proposal_id}] AI 检测: ceiling={ai_check['ceiling']:.2f}, "
                  f"issues={len(ai_check['top_issues'])}")

    result = self._run_critic(
        proposal_id, prop_dir, project_type, round_num,
        critic_writer_timeout_s(section_key),  # v6.8.52: 大模块 1200s，其余 900s
        focus_section=focus_section, is_full_review=is_full_review,
        ai_check_result=ai_check,  # v6.8.7: 传入程序化检测结果
    )
    if not result.get("success"):
        return {"success": False, "error": result.get("error", "critic 失败")}

    # 等待报告落盘
    report_path = prop_dir / "05_review" / f"critic-round-{round_num}.md"
    if not (report_path.exists() and report_path.stat().st_size > 100):
        self._wait_for_critic_report(report_path, timeout=30)

    # 解析报告，决定是否需要 researcher
    # v6.8.3-fix10: references 模块不插入 researcher 链（本身就是文献检验）
    report = self._read_critic_report(prop_dir, round_num)
    if section_key != "references":
        if report["dim_scores"].get("rigor", 1.0) < 0.70 or self._has_lit_gap({"output": report["output"]}):
            self._insert_researcher_pipeline(proposal_id, round_num, section["key"])

    return {"success": True, "score": report["score"]}

def _insert_researcher_pipeline(self, proposal_id: str, round_num: int, section_key: str) -> None:
    """v6.7.12: 在 critic 与 writer 之间插入 researcher 的 4 个子步骤流水线。幂等。"""
    jobs = self._get_jobs(proposal_id)
    writer_id = _make_job_id(proposal_id, round_num, section_key, STEP_WRITER)

    sub_steps = [
        (STEP_GAP_IDENTIFY, STEP_CRITIC),
        (STEP_LIT_SEARCH, STEP_GAP_IDENTIFY),
        (STEP_LIT_READ, STEP_LIT_SEARCH),
        (STEP_LIT_NOTE, STEP_LIT_READ),
    ]

    # 如果已经存在旧版 researcher job，先不动它，保持向后兼容
    researcher_id = _make_job_id(proposal_id, round_num, section_key, STEP_RESEARCHER)
    if self._job_by_id(jobs, researcher_id):
        return

    # 如果任一子步骤已存在，说明已经插入过，直接跳过
    if any(
        self._job_by_id(jobs, _make_job_id(proposal_id, round_num, section_key, step))
        for step, _ in sub_steps
    ):
        return

    # 找到 writer job 的索引
    writer_idx = None
    for i, j in enumerate(jobs):
        if j["job_id"] == writer_id:
            writer_idx = i
            break

    new_jobs = []
    prev_dep = _make_job_id(proposal_id, round_num, section_key, STEP_CRITIC)
    for step, dep in sub_steps:
        job_id = _make_job_id(proposal_id, round_num, section_key, step)
        new_jobs.append({
            "job_id": job_id,
            "proposal_id": proposal_id,
            "step": step,
            "section_key": section_key,
            "round": round_num,
            "status": JOB_STATUS_PENDING,
            "depends_on": [prev_dep],
            "attempts": 0,
            "scheduled_at": "",
            "started_at": "",
            "finished_at": "",
            "last_error": "",
            "cron_job_id": "",
        })
        prev_dep = job_id

    if writer_idx is not None:
        for j in reversed(new_jobs):
            jobs.insert(writer_idx, j)
        # writer 依赖最后一个子步骤
        jobs[writer_idx + len(new_jobs)]["depends_on"].append(prev_dep)
        jobs[writer_idx + len(new_jobs)]["depends_on"] = list(
            dict.fromkeys(jobs[writer_idx + len(new_jobs)]["depends_on"])
        )
    else:
        jobs.extend(new_jobs)

    self._save_jobs(proposal_id, jobs)


def _run_gap_identify_step(self, proposal_id: str, job: Dict[str, Any]) -> Dict[str, Any]:
    """v6.7.12 + v6.8.1: 文献缺口识别。

    混合策略（方案A+B融合）：
    1. 优先尝试 hermes researcher agent loop（方案A）
    2. 失败/超时降级为直接 LLM 调用（方案B，兜底）
    3. 无论成功失败，回写 researcher profile 记忆，促进持续成长
    """
    prop_dir = self._find_proposal_dir(proposal_id)
    if not prop_dir:
        return {"success": False, "error": "proposal 目录不存在"}
    round_num = job["round"]
    section_key = job.get("section_key", "rationale")
    from proposal_sections import PROPOSAL_SECTIONS
    section = next((s for s in PROPOSAL_SECTIONS if s["key"] == section_key), None)
    focus_section = section if section_key != "full_review" else None
    report = self._read_critic_report(prop_dir, round_num)
    critic_output = report.get("output", "")[:3000]

    target_dir = prop_dir / "02_literature" / "gap-analysis"
    target_dir.mkdir(parents=True, exist_ok=True)
    import time as _t
    gap_path = target_dir / f"gap-analysis-r{int(_t.time())}.json"

    section_hint = f"聚焦章节：{focus_section['cn']}\n" if focus_section else ""
    section_name = focus_section['cn'] if focus_section else "整篇"

    # 构建给 researcher 的 agent loop prompt
    agent_prompt = (
        f"你是一位专业研究助手（Researcher）。请分析以下评审报告，"
        f"识别课题「{proposal_id}」在「{section_name}」部分需要补充文献支撑的具体缺口。\n\n"
        f"【评审报告内容】\n{critic_output}\n\n"
        f"请执行：\n"
        f"1. 逐条阅读评审报告中指出的文献/引用/支撑不足问题\n"
        f"2. 对每个问题，明确：论点是什么、缺什么类型的文献、建议检索关键词\n"
        f"3. 忽略与文献无关的问题（如逻辑、格式等）\n"
        f"4. **必须**输出 JSON 格式（不要 markdown 代码块标记，不要其他文字）：\n"
        f'{{"gaps": [{{"claim": "需要支撑的论点", "missing_evidence": "缺少什么证据/文献", "search_keywords": ["关键词1", "关键词2"], "priority": "high"}}]}}\n\n'
        f"示例输出：\n"
        f'{{"gaps": [{{"claim": "固体中HHG效率与晶体对称性的关系尚不清楚", "missing_evidence": "缺乏实验测量不同晶体取向下HHG效率的数据", "search_keywords": ["solid-state HHG crystal orientation", "HHG efficiency anisotropy"], "priority": "high"}}, {{"claim": "Berry曲率对非线性光学的贡献", "missing_evidence": "缺少Berry曲率与高次谐波产生关系的理论计算", "search_keywords": ["Berry curvature harmonic generation", "nonlinear optical Berry phase"], "priority": "medium"}}]}}\n\n'
        f"注意：只输出 JSON，不要输出任何其他文字。如果没有文献缺口，输出空 gaps 数组。"
    )

    # 备用 prompt（直调用，更简洁）
    fallback_prompt = (
        f"请分析以下评审报告，识别需要补充文献支撑的具体缺口。\n\n"
        f"【课题】{proposal_id}\n"
        f"{section_hint}"
        f"【评审报告内容】\n{critic_output}\n\n"
        f"请执行：\n"
        f"1. 逐条阅读评审报告中指出的文献/引用/支撑不足问题\n"
        f"2. 对每个问题，明确：论点是什么、缺什么类型的文献、建议检索关键词\n"
        f"3. 忽略与文献无关的问题（如逻辑、格式等）\n"
        f"4. 直接输出严格 JSON（不要 markdown 代码块），格式如下：\n"
        f"{{\n"
        f"  \"gaps\": [\n"
        f"    {{\n"
        f"      \"claim\": \"需要支撑的论点\",\n"
        f"      \"missing_evidence\": \"缺少什么证据/文献\",\n"
        f"      \"search_keywords\": [\"keyword1\", \"keyword2\"],\n"
        f"      \"priority\": \"high|medium|low\"\n"
        f"    }}\n"
        f"  ]\n"
        f"}}\n"
    )

    # 步骤1：尝试 hermes researcher agent loop
    from hermes_memory import _run_hermes_agent, _write_memory
    agent_result = _run_hermes_agent("researcher", agent_prompt, timeout=300)
    agent_success = agent_result.get("success", False)
    raw_text = ""

    if agent_success:
        raw_text = agent_result.get("output", "")
        # 记录原始输出便于 debug
        if _log:
            _log.info(
                f"[{proposal_id}] gap_identify agent loop 原始输出（{len(raw_text)}字）: "
                f"{raw_text[:500]}"
            )
        if _log:
            _log.info(
                f"[{proposal_id}] gap_identify agent loop 成功 "
                f"elapsed={agent_result.get('elapsed_s', 0)}s"
            )
    else:
        # 步骤2：降级为直接 LLM 调用（兜底）
        if _log:
            _log.warning(
                f"[{proposal_id}] gap_identify agent loop 失败，降级直调: "
                f"{agent_result.get('error', '')}"
            )
        if llm_router is None:
            # 记录失败的记忆
            _write_memory("researcher",
                f"[{now_utc()}] gap_identify 失败（课题：{proposal_id}，轮次：{round_num}，"
                f"章节：{section_name}）— llm_router 未加载"
            )
            return {"success": False, "error": "llm_router 未加载，agent loop 也失败"}

        try:
            call_result = llm_router.call_llm(
                "你是一位严谨的学术研究助手，只输出合法 JSON。",
                [{"role": "user", "content": fallback_prompt}],
                timeout=120,
            )
            raw = call_result[0] if isinstance(call_result, tuple) else call_result
            # v6.8.3: 记录降级事件到 proposal_state
            self._mark_degradation(proposal_id, "gap_identify", "agent_loop_failed→llm_direct")
            raw_text = raw.strip()
        except Exception as e:
            err = str(e)[:300]
            # 记录失败记忆
            _write_memory("researcher",
                f"[{now_utc()}] gap_identify 失败（课题：{proposal_id}，轮次：{round_num}，"
                f"章节：{section_name}）— 直调也失败: {err}"
            )
            if _log:
                _log.warning(f"[{proposal_id}] 文献缺口识别（直调降级）失败: {err}")
            return {"success": False, "error": err}

    # 解析输出
    try:
        text = raw_text.strip()
        if not text:
            if _log:
                _log.warning(f"[{proposal_id}] gap_identify agent 输出为空，跳过")
            # 空 output 时写一个默认空 gap 文件，让后续步骤可以继续
            default_data = {"gaps": [], "note": "agent loop 输出为空，使用 critic 报告原始关键词"}
            gap_path.write_text(json.dumps(default_data, ensure_ascii=False, indent=2), encoding="utf-8")
            return {"success": True, "gap_path": str(gap_path), "method": "empty_fallback", "gap_count": 0}

        if text.startswith("```"):
            lines = text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        # 尝试从文本中提取 JSON（可能嵌在自然语言中）
        data = None
        # 直接解析
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # 尝试找到 JSON 对象
            for start in range(len(text)):
                if text[start] == '{':
                    depth = 0
                    for end in range(start, len(text)):
                        if text[end] == '{':
                            depth += 1
                        elif text[end] == '}':
                            depth -= 1
                            if depth == 0:
                                try:
                                    data = json.loads(text[start:end + 1])
                                    break
                                except json.JSONDecodeError:
                                    pass
                    if data:
                        break

        if not data or not isinstance(data, dict) or "gaps" not in data:
            # agent 返回了非 JSON（自然语言分析），但提取不到 gaps 字段
            # 这通常意味着没有文献缺口，使用空 gaps 兜底让流程继续
            default_data = {"gaps": [], "note": f"agent 未返回标准 JSON gaps 格式，视为无文献缺口。原文前200字: {text[:200]}"}
            gap_path.write_text(json.dumps(default_data, ensure_ascii=False, indent=2), encoding="utf-8")
            if _log:
                _log.info(f"[{proposal_id}] gap_identify agent 未返回 JSON gaps，使用空 gaps 兜底")
            # 仍然写记忆，标记降级
            _write_memory("researcher",
                f"[{now_utc()}] gap_identify 完成（empty_fallback）— 课题：{proposal_id}，"
                f"轮次：{round_num}，章节：{section_name}，agent 未返回标准 JSON"
            )
            return {"success": True, "gap_path": str(gap_path), "method": "empty_fallback", "gap_count": 0}

        gap_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        # 步骤3：回写 researcher profile 记忆
        gap_count = len(data["gaps"])
        high_pri = sum(1 for g in data["gaps"] if g.get("priority") == "high")
        keywords = []
        for g in data["gaps"]:
            keywords.extend(g.get("search_keywords", []))
        keyword_summary = "、".join(list(dict.fromkeys(keywords))[:5])

        method_tag = "agent_loop" if agent_success else "direct_fallback"
        _write_memory("researcher",
            f"[{now_utc()}] gap_identify 完成（{method_tag}）— 课题：{proposal_id}，"
            f"轮次：{round_num}，章节：{section_name}，识别缺口 {gap_count} 个"
            f"（高优先级 {high_pri} 个），关键词：{keyword_summary}"
        )

        if _log:
            _log.info(f"[{proposal_id}] 文献缺口识别完成: {gap_path.name}（{method_tag}）")
        return {"success": True, "gap_path": str(gap_path), "method": method_tag}
    except Exception as e:
        err = str(e)[:300]
        _write_memory("researcher",
            f"[{now_utc()}] gap_identify 解析失败（课题：{proposal_id}，轮次：{round_num}，"
            f"章节：{section_name}）— {err}"
        )
        if _log:
            _log.warning(f"[{proposal_id}] 文献缺口识别解析失败: {err}")
        return {"success": False, "error": err}


def _run_lit_search_step(self, proposal_id: str, job: Dict[str, Any]) -> Dict[str, Any]:
    """v6.7.12 + v6.8.1: 针对文献缺口的检索。

    混合策略（方案A+B融合）：
    1. 优先尝试 hermes researcher agent loop 联网检索
    2. 失败/超时降级为 LiteratureService.search()（兜底）
    3. 无论成功失败，回写 researcher profile 记忆
    """
    prop_dir = self._find_proposal_dir(proposal_id)
    if not prop_dir:
        return {"success": False, "error": "proposal 目录不存在"}
    round_num = job["round"]
    section_key = job.get("section_key", "rationale")
    from proposal_sections import PROPOSAL_SECTIONS
    section = next((s for s in PROPOSAL_SECTIONS if s["key"] == section_key), None)
    focus_section = section if section_key != "full_review" else None
    section_name = focus_section['cn'] if focus_section else "整篇"

    # 找到本轮最新的 gap-analysis JSON
    gap_dir = prop_dir / "02_literature" / "gap-analysis"
    gap_files = sorted(gap_dir.glob("gap-analysis-r*.json"), reverse=True)
    if not gap_files:
        return {"success": False, "error": "未找到 gap analysis 文件"}
    gap_path = gap_files[0]

    import json
    gap_data = json.loads(gap_path.read_text(encoding="utf-8"))
    gaps = gap_data.get("gaps", [])
    all_keywords = []
    for g in gaps:
        all_keywords.extend(g.get("search_keywords", []))
    gap_keywords = list(dict.fromkeys(all_keywords))[:10]
    keyword_str = "、".join(gap_keywords)

    # 步骤1：尝试 hermes researcher agent loop 联网检索
    from hermes_memory import _run_hermes_agent, _write_memory
    agent_success = False
    papers = []

    # 复用 LiteratureService 的去重机制：获取已有论文 ID 集合
    from literature_service import LiteratureService
    _svc = LiteratureService()
    _local_ids = set(_svc._scan_local_raw_papers().keys())
    _exclude_ids = _svc._get_exclude_ids(proposal_id)
    _all_known = _local_ids | _exclude_ids
    _exclude_count = len(_all_known)

    # 构建 exclude_prompt 注入 agent prompt（复用简报去重策略）
    _exclude_prompt = ""
    if _all_known:
        _exclude_prompt = (
            f"\n\n【请跳过以下已处理论文（共 {_exclude_count} 篇）】\n"
            + "\n".join(sorted(str(x) for x in _all_known))
        )

    # v6.8.14 WP4: KB-first 三层预检索——注入本地知识库上下文作为背景
    _kb_context_block = ""
    try:
        _kb_context = _svc.get_context(gap_keywords=gap_keywords, proposal_id=proposal_id)
        if _kb_context and len(_kb_context) > 50:
            _kb_context_block = (
                f"\n\n【本地知识库已有的相关文献和概念（供参考，不要重复检索这些）】\n"
                f"{_kb_context[:3000]}\n"
            )
    except Exception as e:
        if _log:
            _log.warning(f"KB context 注入失败（继续）: {e}")

    agent_prompt = (
        f"你是一位专业研究助手（Researcher）。请针对课题「{proposal_id}」的"
        f"「{section_name}」部分，检索以下关键词的最新论文。\n\n"
        f"【检索关键词】\n{keyword_str}\n"
        f"{_exclude_prompt}\n"
        f"{_kb_context_block}\n\n"
        f"请执行：\n"
        f"1. 使用 web_search 工具逐一检索每个关键词\n"
        f"2. 对每篇论文，提取完整信息：arxiv_id、标题、作者、年份、TL;DR\n"
        f"3. 优先选择 2024-2026 年的最新论文\n"
        f"4. **必须**输出 JSON 数组格式（不要 markdown 代码块标记，不要其他格式）：\n"
        f"   [{{\"arxiv_id\": \"2403.15337\", \"title\": \"论文标题\", \"authors\": \"作者等\", \"year\": \"2024\", \"score\": 0.9, \"tldr\": \"一句话摘要\"}}]\n\n"
        f"示例输出：\n"
        f'[{{"arxiv_id": "2401.12345", "title": "Strong-field HHG in solids", "authors": "Zhang et al.", "year": "2024", "score": 0.85, "tldr": "发现固体高次谐波产生的新机制"}}]'
        f'\n[{{"arxiv_id": "2402.67890", "title": "Berry phase effects in ultrafast dynamics", "authors": "Li et al.", "year": "2024", "score": 0.80, "tldr": "贝里相位在超快动力学中的作用"}}]\n\n'
        f"注意：只输出 JSON 数组，不要输出任何其他文字。如果检索不到论文，输出空数组 []。"
    )

    try:
        agent_result = _run_hermes_agent("researcher", agent_prompt, timeout=360)
        if agent_result.get("success"):
            agent_success = True
            output = agent_result.get("output", "")
            # 记录原始输出前 500 字，便于 debug 解析失败原因
            if _log:
                _log.info(
                    f"[{proposal_id}] lit_search agent loop 原始输出（{len(output)}字）: "
                    f"{output[:500]}"
                )
            papers = _svc._parse_researcher_output(output)
            # 复用去重：按 arxiv_id 比对本地知识库，准确标记 is_new
            for p in papers:
                aid = p.get("arxiv_id", "")
                p["is_new"] = bool(aid and aid not in _local_ids)
            if _log:
                _log.info(
                    f"[{proposal_id}] lit_search agent loop 成功，"
                    f"解析到 {len(papers)} 篇论文"
                )
    except Exception as e:
        if _log:
            _log.warning(f"[{proposal_id}] lit_search agent loop 异常: {e}")

    # 步骤2：如果 agent loop 失败（非成功），降级为 LiteratureService
    # 注意：agent 成功但解析 0 篇不触发降级（可能确实无新论文）
    if not agent_success:
        if _log:
            _log.warning(
                f"[{proposal_id}] lit_search agent loop 失败，降级 LiteratureService"
            )
        # v6.8.3: 记录降级事件
        self._mark_degradation(proposal_id, "lit_search", "agent_loop_failed→LiteratureService")
        try:
            papers = _svc.search(
                keywords=gap_keywords, source="pipeline", proposal_id=proposal_id
            )
        except Exception as e:
            err = str(e)[:300]
            _write_memory("researcher",
                f"[{now_utc()}] lit_search 失败（课题：{proposal_id}，轮次：{round_num}，"
                f"章节：{section_name}）— 降级检索也失败: {err}"
            )
            if _log:
                _log.warning(f"[{proposal_id}] lit_search 降级检索失败: {err}")
            return {"success": False, "error": err}

    # 写入 lit-gap-*.md 文件
    target_dir = prop_dir / "02_literature" / "targeted-research"
    target_dir.mkdir(parents=True, exist_ok=True)
    import time as _t
    result_path = target_dir / f"lit-gap-{int(_t.time())}.md"

    lines = [f"# 定向文献检索报告\n", f"## 课题\n{proposal_id}\n"]
    lines.append(f"## 检索关键词\n- {keyword_str}\n")
    lines.append(f"## 检索结果\n")
    for p in papers:
        arxiv_id = p.get("arxiv_id", "")
        title = p.get("title", "")
        authors = p.get("authors", "")
        year = p.get("year", "")
        score = p.get("score", 0.5)
        tldr = p.get("tldr", "")
        source_tag = "本地知识库" if not p.get("is_new", True) else "联网检索"
        lines.append(f"- {arxiv_id} | {title} | {authors} | {year} | {score} | {tldr} | 来源：{source_tag}")

    result_path.write_text("\n".join(lines), encoding="utf-8")

    # 步骤3：新论文入库到 knowledge/raw/papers/
    new_papers = [p for p in papers if p.get("is_new", False)]
    if new_papers:
        try:
            ingest_res = _svc._ingest_new_papers(new_papers, source="pipeline", proposal_id=proposal_id)
            # v6.8.20: 用真实入库数替代之前虚报的"len(new_papers)"
            # 修复前：build_frontmatter 对含 dict 元素的列表抛 unhashable type，
            # 所有论文静默失败，但外层 try/except 永远不触发，导致日志与实际不一致。
            if _log:
                _log.info(
                    f"[{proposal_id}] lit_search 新入库 "
                    f"{ingest_res['ingested']}/{len(new_papers)} 篇论文到知识库 "
                    f"（failed={ingest_res['failed']}, skipped={ingest_res['skipped']}）"
                )
        except Exception as e:
            if _log:
                _log.warning(f"[{proposal_id}] lit_search 新论文入库失败: {e}")

    # 步骤4：回写 researcher profile 记忆
    method_tag = "agent_loop" if agent_success else "direct_fallback"
    paper_count = len(papers)
    paper_ids = [p.get("arxiv_id", "") for p in papers[:5] if p.get("arxiv_id")]
    paper_summary = "、".join(paper_ids) if paper_ids else "无"
    _write_memory("researcher",
        f"[{now_utc()}] lit_search 完成（{method_tag}）— 课题：{proposal_id}，"
        f"轮次：{round_num}，章节：{section_name}，关键词：{keyword_str}，"
        f"检索到 {paper_count} 篇论文，示例：{paper_summary}"
    )

    if _log:
        _log.info(f"[{proposal_id}] lit_search 完成: {result_path.name}（{method_tag}）")
    # agent 成功执行即视为 success（0 篇论文不等于失败）
    return {"success": True, "result_path": str(result_path), "method": method_tag, "paper_count": len(papers)}


def _run_lit_read_step(self, proposal_id: str, job: Dict[str, Any]) -> Dict[str, Any]:
    """v6.7.12 + v6.8.1: 文献深度阅读。

    混合策略（方案A+B融合）：
    1. 优先尝试 hermes researcher agent loop 深度阅读
    2. 失败/超时降级为 LiteratureService.read()（兜底）
    3. 无论成功失败，回写 researcher profile 记忆
    """
    prop_dir = self._find_proposal_dir(proposal_id)
    if not prop_dir:
        return {"success": False, "error": "proposal 目录不存在"}

    # 找到本轮最新的 lit-gap 报告
    targeted_dir = prop_dir / "02_literature" / "targeted-research"
    lit_files = sorted(targeted_dir.glob("lit-gap-*.md"), reverse=True)
    if not lit_files:
        return {"success": False, "error": "未找到文献检索报告"}
    lit_path = lit_files[0]

    import re
    text = lit_path.read_text(encoding="utf-8")
    arxiv_ids = re.findall(r"(\d{4}\.\d{4,5})", text)

    if not arxiv_ids:
        if _log:
            _log.info(f"[{proposal_id}] lit_read 跳过: 无 arxiv_id 可读（lit_search 未返回论文）")
        return {"success": True, "notes_path": "", "read_count": 0, "reason": "无论文可读"}

    notes = []
    read_count = 0
    agent_success = False

    # 步骤1：尝试 hermes researcher agent loop 深度阅读（每篇论文单独派活）
    from hermes_memory import _run_hermes_agent, _write_memory

    for aid in arxiv_ids[:5]:  # 每轮最多深度阅读 5 篇，避免超时
        agent_prompt = (
            f"你是一位专业研究助手（Researcher）。请深度阅读以下论文"
            f"（课题：{proposal_id}），并整理为结构化笔记。\n\n"
            f"【arXiv ID】{aid}\n\n"
            f"请执行：\n"
            f"1. 使用 web_search 获取论文的完整信息（标题、作者、摘要等）\n"
            f"2. 输出必须包含以下五个维度，每个维度不少于 3 句实质内容：\n"
            f"   ## 研究问题（Research Question）\n"
            f"   论文的核心研究问题、目标或中心论点（the research question, aim, or central argument）。\n\n"
            f"   ## 研究背景（Background）\n"
            f"   该问题的学术背景、前人工作、领域现状及研究动机（the background of the question）。\n\n"
            f"   ## 研究方法（Methods）\n"
            f"   数据来源、实验方法、理论框架或技术路线（data and method）。\n\n"
            f"   ## 主要发现与核心结论（Main Results）\n"
            f"   关键结果、定量发现、核心结论与图表数据（main results and findings）。\n\n"
            f"   ## 潜在研究方向（Future Directions）\n"
            f"   研究局限性、注意事项及未解决的开放问题（limitations, caveats, and open questions）。\n"
        )
        try:
            agent_result = _run_hermes_agent("researcher", agent_prompt, timeout=240)
            if agent_result.get("success"):
                agent_success = True
                output = agent_result.get("output", "")
                notes.append(f"## {aid}\n\n{output}\n")
                read_count += 1
                # v6.8.18 fix: 成功路径下也要建立 wiki/papers/{aid}.md 页面，
                # 否则后续 lit_note.link_to_proposal() 会因 wiki 页面不存在而返回 False，
                # 导致 used_by_proposals 反向链接断裂。仅在页面尚不存在时写入，避免覆盖既有深度笔记。
                try:
                    from literature_service import LiteratureService
                    svc = LiteratureService()
                    existing = svc._get_wiki_paper_note(aid)
                    if not existing:
                        svc._save_wiki_paper_note(aid, output, proposal_id)
                        svc._update_read_status(aid, "deep-read", proposal_id)
                except Exception as wiki_e:
                    if _log:
                        _log.warning(
                            f"[{proposal_id}] lit_read 成功但 wiki 写入失败 {aid}: {wiki_e}"
                        )
                if _log:
                    _log.info(f"[{proposal_id}] lit_read agent loop 成功: {aid}")
            else:
                # agent loop 失败，对该论文降级为 LiteratureService
                if _log:
                    _log.warning(
                        f"[{proposal_id}] lit_read agent loop 失败 {aid}，降级直读: "
                        f"{agent_result.get('error', '')}"
                    )
                try:
                    from literature_service import LiteratureService
                    svc = LiteratureService()
                    result = svc.read(aid, proposal_id=proposal_id)
                    if result.get("content"):
                        notes.append(f"## {aid}\n\n{result['content']}\n")
                        read_count += 1
                except Exception as e2:
                    if _log:
                        _log.warning(f"[{proposal_id}] lit_read 降级直读失败 {aid}: {e2}")
        except Exception as e:
            if _log:
                _log.warning(f"[{proposal_id}] lit_read agent loop 异常 {aid}: {e}")
            # 异常时降级
            try:
                from literature_service import LiteratureService
                svc = LiteratureService()
                result = svc.read(aid, proposal_id=proposal_id)
                if result.get("content"):
                    notes.append(f"## {aid}\n\n{result['content']}\n")
                    read_count += 1
            except Exception:
                pass

    # 如果 agent loop 完全没有成功，对所有论文执行一次批量降级
    if not agent_success and read_count == 0:
        if _log:
            _log.warning(
                f"[{proposal_id}] lit_read agent loop 全部失败，批量降级 LiteratureService"
            )
        try:
            from literature_service import LiteratureService
            svc = LiteratureService()
            for aid in arxiv_ids[:5]:
                result = svc.read(aid, proposal_id=proposal_id)
                if result.get("content"):
                    notes.append(f"## {aid}\n\n{result['content']}\n")
                    read_count += 1
        except Exception as e:
            err = str(e)[:300]
            _write_memory("researcher",
                f"[{now_utc()}] lit_read 失败（课题：{proposal_id}）— "
                f"批量降级也失败: {err}"
            )
            return {"success": False, "error": err}

    notes_path = prop_dir / "02_literature" / "reading-notes.md"
    notes_path.parent.mkdir(parents=True, exist_ok=True)
    if notes:
        notes_path.write_text("\n\n".join(notes), encoding="utf-8")

    # 步骤2：回写 researcher profile 记忆
    method_tag = "agent_loop" if agent_success else "direct_fallback"
    _write_memory("researcher",
        f"[{now_utc()}] lit_read 完成（{method_tag}）— 课题：{proposal_id}，"
        f"论文 {read_count}/{len(arxiv_ids[:5])} 篇，"
        f"论文ID：{'、'.join(arxiv_ids[:3])}"
    )

    if _log:
        _log.info(f"[{proposal_id}] lit_read 完成: {read_count} 篇（{method_tag}）")
    return {"success": True, "notes_path": str(notes_path), "read_count": read_count, "method": method_tag}


def _run_lit_note_step(self, proposal_id: str, job: Dict[str, Any]) -> Dict[str, Any]:
    """v6.7.12: 将阅读笔记整理并导入课题文献库。

    改造：通过 LiteratureService.link_to_proposal() 统一关联。
    """
    prop_dir = self._find_proposal_dir(proposal_id)
    if not prop_dir:
        return {"success": False, "error": "proposal 目录不存在"}

    targeted_dir = prop_dir / "02_literature" / "targeted-research"
    lit_files = sorted(targeted_dir.glob("lit-gap-*.md"), reverse=True)
    if lit_files:
        try:
            import re
            from literature_service import LiteratureService
            svc = LiteratureService()

            text = lit_files[0].read_text(encoding="utf-8")
            arxiv_ids = re.findall(r"(\d{4}\.\d{4,5})", text)

            imported = 0
            for aid in arxiv_ids:
                if svc.link_to_proposal(aid, proposal_id, citation_location="adversarial-review"):
                    imported += 1

            if _log and imported:
                _log.info(f"[{proposal_id}] 已关联 {imported} 篇论文到课题")
            return {"success": True, "imported": imported}
        except Exception as e:
            if _log:
                _log.warning(f"[{proposal_id}] 关联论文到课题失败: {e}")
            return {"success": False, "error": str(e)}
    if _log:
        _log.info(f"[{proposal_id}] lit_note 跳过: 无检索报告可导入")
    return {"success": True, "imported": 0, "reason": "无检索报告可导入", "skipped": True}


def _run_researcher_step(self, proposal_id: str, job: Dict[str, Any]) -> Dict[str, Any]:
    """向后兼容：旧版 researcher job 仍然执行完整流程。"""
    prop_dir = self._find_proposal_dir(proposal_id)
    if not prop_dir:
        return {"success": False, "error": "proposal 目录不存在"}
    round_num = job["round"]
    section_key = job.get("section_key", "rationale")
    from proposal_sections import PROPOSAL_SECTIONS
    section = next((s for s in PROPOSAL_SECTIONS if s["key"] == section_key), None)
    focus_section = section if section_key != "full_review" else None
    report = self._read_critic_report(prop_dir, round_num)
    critic_result = {"output": report["output"], "success": True}
    lit = self._run_researcher_targeted(
        proposal_id, prop_dir, critic_result, focus_section, timeout=1200
    )
    return {"success": bool(lit), "lit_path": lit}

def _run_writer_step(self, proposal_id: str, job: Dict[str, Any]) -> Dict[str, Any]:
    """执行 writer 并更新 lifecycle 状态（轮次、分数、section_passes）。"""
    prop_dir = self._find_proposal_dir(proposal_id)
    if not prop_dir:
        return {"success": False, "error": "proposal 目录不存在"}

    prop_state = self._get_proposal_state(proposal_id)
    project_type = prop_state.get("project_type", "general")
    round_num = job["round"]
    section_key = job.get("section_key", "rationale")
    from proposal_sections import PROPOSAL_SECTIONS
    section = next((s for s in PROPOSAL_SECTIONS if s["key"] == section_key), None)
    focus_section = section if section_key != "full_review" else None
    is_full_review = section_key == "full_review"
    threshold = self._get_quality_threshold(project_type)

    # 读取本轮 critic 报告
    report = self._read_critic_report(prop_dir, round_num)
    dim_scores = report["dim_scores"]
    weakest_dim = self._get_weakest_dimension(dim_scores)

    # v6.7.6: writer 修改前备份当前申请书，供 monitor 比对
    proposal_path = prop_dir / "04_proposal" / "proposal-draft.md"
    backup_path = prop_dir / "04_proposal" / f"proposal-draft-r{round_num - 1}.md"
    if proposal_path.exists() and proposal_path.stat().st_size > 100:
        try:
            shutil.copy2(str(proposal_path), str(backup_path))
        except Exception:
            pass

    # 构造 lit_supplement：使用本 proposal 下 targeted-research 目录最新文件
    lit_supplement = ""
    targeted_dir = prop_dir / "02_literature" / "targeted-research"
    if targeted_dir.exists():
        lit_files = sorted(targeted_dir.glob("lit-gap-*.md"), reverse=True)
        if lit_files:
            lit_supplement = (
                f"\n【文献补充（researcher 定向检索）】\n"
                f"请参考 {lit_files[0]} 中的新文献，在修订时引用。\n"
            )

    # v6.9.30: 程序化 AI 写作模式检测——writer 步骤重新运行（与 critic 步骤
    # 结果一致，确定性），注入 writer prompt 并用于后续评分 cap
    from proposal_sections import ProposalSections
    sections_obj = ProposalSections(prop_dir / "04_proposal")
    sections_obj.ensure_split()
    ai_check = self._detect_ai_patterns(prop_dir, sections_obj)
    # v6.9.47: 章节级基线——writer 每轮只修聚焦章节，全局口径会被其余两章
    # 稀释（单章节修复完美，全局天花板仍不动，复检误判）。正文章节 job
    # 额外记录该章节自身的原始天花板作为复检归因基线。
    section_baseline = None
    if section_key in ("rationale", "content", "scheme"):
        try:
            section_baseline = self._detect_ai_patterns(
                prop_dir, sections_obj, section_key=section_key
            )
        except Exception:
            section_baseline = None

    writer_result = self._run_writer_optimize(
        proposal_id, prop_dir, project_type,
        critic_result={"output": report["output"]},
        timeout=critic_writer_timeout_s(section_key),  # v6.8.52: 大模块 1200s，其余 900s
        weakest_dim=weakest_dim,
        dim_scores=dim_scores,
        focus_section=focus_section,
        is_full_review=is_full_review,
        lit_supplement=lit_supplement,
        ai_check_result=ai_check,  # v6.8.7: writer 必须修复检测到的 AI 模式问题
    )
    if not writer_result.get("success"):
        return {"success": False, "error": writer_result.get("error", "writer 失败")}

    # v6.9.33: writer 后程序化复检——AI 天花板必须提升（防表面修改闭环）
    # 背景：writer prompt 已注入 top_issues 明细，但历史执行不力（moire 案例
    # 只修 1/7 问题）。复检用确定性检测验证 writer 是否实质修复表达问题：
    # 未达标（<0.85）必须严格提升；已达标只要求不显著倒退；references 轮跳过
    # （不涉及正文表达）。
    # v6.9.47 两项口径修复（attosecond 课题 5 连误判根因）：
    #   ① raw 比较——floor(0.5) 会把 0.6→0.5 的实质改善掩埋成 0.50→0.50，
    #     复检改用 floor 前原始值（raw_ceiling），真实进步可见；
    #   ② 章节级归因——章节级 job 只修聚焦章节，全局口径被其余章节稀释，
    #     复检以聚焦章节自身变化为准（无基线时回退全局口径）。
    ai_check_after = None
    expression_improved = True
    expression_not_improved_reason = ""
    if section_key != "references" and ai_check:
        ai_check_after = self._detect_ai_patterns(prop_dir, sections_obj)
        ceiling_before = ai_check.get("ceiling", 1.0)
        ceiling_after = ai_check_after.get("ceiling", 1.0)
        raw_before = ai_check.get("raw_ceiling", ceiling_before)
        raw_after = ai_check_after.get("raw_ceiling", ceiling_after)

        # 章节级归因：聚焦章节自身口径（有基线时优先）
        section_after = None
        if section_baseline and section_key in ("rationale", "content", "scheme"):
            try:
                section_after = self._detect_ai_patterns(
                    prop_dir, sections_obj, section_key=section_key
                )
            except Exception:
                section_after = None

        if section_baseline and section_after:
            sec_raw_b = section_baseline.get("raw_ceiling", section_baseline.get("ceiling", 1.0))
            sec_raw_a = section_after.get("raw_ceiling", section_after.get("ceiling", 1.0))
            if sec_raw_b >= 0.85:
                expression_improved = sec_raw_a >= sec_raw_b - 0.02
            else:
                expression_improved = sec_raw_a > sec_raw_b + 0.001
            if not expression_improved:
                expression_not_improved_reason = (
                    f"writer 未实质修复表达问题（{section_key} 章节原始天花板 "
                    f"{sec_raw_b:.2f}→{sec_raw_a:.2f}，全局 {raw_before:.2f}→{raw_after:.2f}）"
                )
        else:
            if raw_before >= 0.85:
                expression_improved = raw_after >= raw_before - 0.02
            else:
                expression_improved = raw_after > raw_before + 0.001
            if not expression_improved:
                expression_not_improved_reason = (
                    f"writer 未实质修复表达问题（AI 原始天花板 {raw_before:.2f}→{raw_after:.2f}，"
                    f"floor 后 {ceiling_before:.2f}→{ceiling_after:.2f}）"
                )
        if not expression_improved:
            if _log:
                _log.warning(f"[{proposal_id}] {expression_not_improved_reason}")

    # 重新读取报告计算分数（writer 不应修改 critic 报告）
    report = self._read_critic_report(prop_dir, round_num)
    score_after = report["score"]
    dim_scores = report["dim_scores"]
    weakest_dim = self._get_weakest_dimension(dim_scores)
    issues = report["issues"]

    # v6.9.30: 程序化天花板强制执行——表达质量得分不得超过 AI 检测产出的天花板
    # （与 optimize.py 的 _run_optimization_round 对齐，微调度器路径此前缺失）
    if ai_check and "expression" in dim_scores:
        ceiling = ai_check.get("ceiling", 1.0)
        if dim_scores["expression"] > ceiling:
            if _log:
                _log.warning(
                    f"[{proposal_id}] 表达质量 {dim_scores['expression']:.2f} > 天花板 {ceiling:.2f}，"
                    f"强制 cap 至 {ceiling:.2f}"
                )
            dim_scores["expression"] = ceiling
            score_after = self._recalculate_score(dim_scores, project_type)

    # v6.8.8: 综合分天花板——scoring_integrity_rules.rule_1
    if ai_check:
        ai_ceiling = ai_check.get("ceiling", 1.0)
        overall_ceiling = 1.0
        if ai_ceiling < 0.7:
            overall_ceiling = 0.75
        elif ai_ceiling < 0.8:
            overall_ceiling = 0.80
        elif ai_ceiling < 0.9:
            overall_ceiling = 0.85
        if score_after > overall_ceiling:
            if _log:
                _log.warning(
                    f"[{proposal_id}] 综合分 {score_after:.2f} > 综合天花板 {overall_ceiling:.2f}"
                    f"（AI天花板={ai_ceiling:.2f}），强制 cap"
                )
            score_after = overall_ceiling

    # v6.8.8: references 评审专用计分——N/A 维度不纳入加权
    if section_key == "references" and dim_scores:
        ref_dims = {k: v for k, v in dim_scores.items() if k in ("rigor", "completeness") and v > 0}
        if ref_dims:
            score_after = sum(ref_dims.values()) / len(ref_dims)
            if _log:
                _log.info(f"[{proposal_id}] references 评审专用计分: {score_after:.2f} (dims={ref_dims})")

    # v6.9.25: 锚点对比结论与评分档位强制绑定——范本锚点成为分数锚
    # v6.9.28: references 评审跳过绑定（口径为文献元数据准确性，写作语体锚点不适用）
    anchor_conclusion = ""
    if section_key != "references":
        anchor_conclusion = self._extract_anchor_conclusion(report["output"])
        score_after = self._apply_anchor_conclusion_binding(
            proposal_id, report["output"], dim_scores, score_after, project_type
        )

    # v6.8.8: 评审报告完整性验证——anti_superficial_review.programmatic_validation
    report_invalid_reason = ""
    report_path = prop_dir / "05_review" / f"critic-round-{round_num}.md"
    if report_path.exists() and report_path.stat().st_size > 100:
        try:
            report_content = report_path.read_text(encoding="utf-8")
            has_anchor = "锚点对比" in report_content or "范本对标" in report_content
            has_style = "写作风格" in report_content
            if section_key != "references":
                if not has_anchor:
                    report_invalid_reason = "缺少'锚点对比'段落"
                elif not has_style:
                    report_invalid_reason = "缺少'写作风格评估'段落"
            if report_invalid_reason and _log:
                _log.warning(f"[{proposal_id}] 评审报告不完整: {report_invalid_reason}")
        except Exception:
            pass

    # v6.8.22: P0 跨轮持久化——本轮 critic 出现的 critical/high 问题写入 open_critical_issues
    # 供下一轮 critic/writer prompt 注入，实现跨轮记忆（断裂点3）
    try:
        self._update_open_critical_issues(
            proposal_id, issues, round_num, section_key,
        )
    except Exception:
        if _log:
            _log.warning(f"[{proposal_id}] 更新 open_critical_issues 失败（非关键路径）")

    min_score = threshold.get("min_overall_score", 0.85)
    weak_dims = [k for k, floor in self.DIMENSION_FLOOR.items() if k in dim_scores and dim_scores[k] < floor]
    section_passed = (
        score_after >= min_score
        and len(weak_dims) == 0
        and not report_invalid_reason
        and expression_improved  # v6.9.33: writer 后表达天花板必须提升（防表面修改）
    )

    score_before = prop_state.get("last_score", 0.0)

    # 更新 proposal 状态（writer 只记录本轮输出质量，不推进轮次；轮次在 monitor 收尾后推进）
    prop_state = self._get_proposal_state(proposal_id)
    prop_state["last_score"] = score_after
    prop_state["last_dim_scores"] = dim_scores
    section_passes = prop_state.get("section_passes", {})
    section_passes[section_key] = section_passed
    prop_state["section_passes"] = section_passes
    prop_state["score_history"].append({
        "round": round_num,
        "score": score_after,
        "dim_scores": dim_scores,
        "weakest_dim": weakest_dim,
        "focus_section": section_key,
        "section_passed": section_passed,
        "issues_count": len(issues),
        "high_issues": sum(1 for i in issues if i.get("severity") == "high"),
        # v6.9.30: 程序化 AI 检测摘要随轮次入史——prompt_optimizer 聚合
        # 全局 top_issues 生成针对性修复指令（与 optimize.py 对齐）
        "ai_ceiling": round(ai_check.get("ceiling", 1.0), 3),
        # v6.9.33: writer 后复检天花板 + 是否实质提升——防表面修改闭环可观测
        "ai_ceiling_after": round(ai_check_after.get("ceiling", 1.0), 3) if ai_check_after else None,
        "expression_improved": expression_improved,
        "expression_not_improved_reason": expression_not_improved_reason,
        "ai_top_issues": (ai_check.get("top_issues") or [])[:6],
        # v6.9.30: 锚点对比结论随轮次入史——范本引导效果可观测
        # （达标/基本接近/差距明显；references 轮为空串）
        "anchor_conclusion": anchor_conclusion,
        "at": now_utc(),
    })
    prop_state["updated_at"] = now_utc()
    self._set_proposal_state(proposal_id, prop_state)

    try:
        self.update_proposal_brief(proposal_id)
    except Exception:
        pass

    # v6.7.6: 达标判定与流转移至 monitor 步骤，由 monitor 综合评估后决定
    return {
        "success": True,
        "round": round_num,
        "score_before": score_before,
        "score_after": score_after,
        "section_passed": section_passed,
        # v6.9.33: 复检结果随返回传递，monitor 可据此综合评估
        "expression_improved": expression_improved,
        "expression_not_improved_reason": expression_not_improved_reason,
    }


# ────────────────────────────────────────────────────────────────────
# v6.8.26: 研究设想质量门槛（idea_review）
# ────────────────────────────────────────────────────────────────────

def _run_idea_review_step(self, proposal_id: str, job: Dict[str, Any]) -> Dict[str, Any]:
    """v6.8.26: 研究设想独立评审——进入 optimizing 前的质量门槛。

    流程：
    1. researcher profile 对 00_research_idea.md 做独立评审
    2. 评审聚焦：科学问题清晰度、创新点可检验性、研究内容与方案的逻辑切分
    3. 分数 ≥ 0.70 → 通过，后续 critic-writer 链继续执行
    4. 分数 < 0.70 → writer 根据评审意见修改研究设想，重新评审
    5. 最多 3 轮迭代，仍不达标则返回失败（proposal 卡住，等待人工介入）

    此步骤在 round 1 的 job 链最前端，作为所有 critic 的前置依赖。
    也可在 monitor 检测到结构性缺陷时重新触发（round > 1）。
    """
    prop_dir = self._find_proposal_dir(proposal_id)
    if not prop_dir:
        return {"success": False, "error": "proposal 目录不存在"}

    idea_path = prop_dir / "00_research_idea.md"
    if not idea_path.exists():
        return {"success": False, "error": "研究设想文件不存在"}

    prop_state = self._get_proposal_state(proposal_id)
    if not prop_state:
        return {"success": False, "error": "proposal 状态不存在"}

    round_num = job.get("round", 0)
    attempts = prop_state.get("idea_review_attempts", 0)

    # ── 评审循环 ──
    for attempt in range(1, MAX_IDEA_REVIEW_ATTEMPTS + 1):
        idea_content = idea_path.read_text(encoding="utf-8")

        # 1. 调用 researcher 评审研究设想
        review_prompt = (
            f"请对以下 NSFC 课题研究设想做独立质量评审。\n\n"
            f"【研究设想文件】\n{idea_path}\n"
            f"请读取该文件并做评审。\n\n"
            f"评审维度（每维 0-1 分）：\n"
            f"1. 科学问题清晰度（clarity）：核心科学问题是否明确、聚焦，"
            f"能否用一两句话概括，是否避免了泛化或模糊表述\n"
            f"2. 创新点可检验性（testability）：每个创新点是否有对应的"
            f"可检验指标或实验信号，能否被证伪\n"
            f"3. 内容-方案逻辑切分（coherence）：研究内容（做什么）与"
            f"研究方案（怎么做）是否有清晰边界，是否存在文件级重复、"
            f"模块空置或逻辑交叉\n"
            f"4. 方向一致性（consistency）：各子方向是否服务于同一核心"
            f"科学问题，是否存在拼凑感\n\n"
            f"请给出每个维度的分数和具体问题，并在报告末尾包含评分块：\n"
            f"```\n"
            f"## 评分\n"
            f"科学问题清晰度：0.75\n"
            f"创新点可检验性：0.70\n"
            f"内容方案切分：0.65\n"
            f"方向一致性：0.80\n"
            f"综合评分：0.73\n"
            f"```\n"
            f"将评审报告写入：{prop_dir / '05_review' / f'idea-review-r{round_num}-a{attempt}.md'}\n"
        )
        # v6.9.45: 600s→1200s。idea_review 要求 researcher 联网核查文献
        # 可靠性（Crossref/arXiv 题名检索，a3 评审明确使用），实测 600s
        # 反复超时（08-24 v2 设想重评 elapsed=600.06s 精确卡线）。与
        # critic 1200s 基准对齐。
        review_result = self._run_hermes("researcher", review_prompt, timeout=1200)
        if not review_result.get("success"):
            return {"success": False, "error": f"评审调用失败：{review_result.get('error')}"}

        # 2. 解析评审分数
        report_path = prop_dir / "05_review" / f"idea-review-r{round_num}-a{attempt}.md"
        score = 0.0
        issues = ""
        if report_path.exists():
            report_text = report_path.read_text(encoding="utf-8")
            score, issues = _parse_idea_review_score(report_text)
        else:
            # 等待报告落盘
            import time
            for _ in range(6):
                time.sleep(5)
                if report_path.exists():
                    report_text = report_path.read_text(encoding="utf-8")
                    score, issues = _parse_idea_review_score(report_text)
                    break

        # 3. 更新 proposal 状态
        prop_state = self._get_proposal_state(proposal_id) or {}
        prop_state["idea_review_attempts"] = attempt
        prop_state["idea_review_score"] = score
        prop_state["idea_review_issues"] = issues[:500]
        prop_state["idea_review_at"] = now_utc()
        self._set_proposal_state(proposal_id, prop_state)

        # 4. 达标 → 通过
        if score >= IDEA_REVIEW_THRESHOLD:
            if _log:
                _log.info(
                    f"[{proposal_id}] 研究设想评审通过 "
                    f"(attempt={attempt}, score={score:.2f})"
                )
            prop_state["idea_review_passed"] = True
            self._set_proposal_state(proposal_id, prop_state)
            return {
                "success": True,
                "idea_review_score": score,
                "attempts": attempt,
                "passed": True,
            }

        # 5. 未达标且还有重试机会 → writer 修改研究设想
        if attempt < MAX_IDEA_REVIEW_ATTEMPTS:
            if _log:
                _log.warning(
                    f"[{proposal_id}] 研究设想评审未达标 "
                    f"(attempt={attempt}, score={score:.2f} < {IDEA_REVIEW_THRESHOLD}), "
                    f"触发 writer 修复"
                )
            fix_prompt = (
                f"请根据以下评审意见修改研究设想文件。\n\n"
                f"【待修改文件】{idea_path}\n"
                f"请读取该文件，根据评审意见做针对性修改。\n\n"
                f"【评审意见】\n{issues}\n\n"
                f"要求：\n"
                f"1. 针对评审指出的每个问题做具体修改，不要泛泛而谈\n"
                f"2. 修改后确保科学问题更聚焦、创新点可检验、"
                f"研究内容与方案有清晰边界\n"
                f"3. 不要改变研究方向，只优化表述和逻辑切分\n"
                f"4. 直接写入文件 {idea_path}\n"
            )
            fix_result = self._run_hermes("writer", fix_prompt, timeout=600)
            if not fix_result.get("success"):
                return {"success": False, "error": f"修复调用失败：{fix_result.get('error')}"}
        else:
            # 6. 超过最大重试次数 → 失败
            if _log:
                _log.error(
                    f"[{proposal_id}] 研究设想评审 {MAX_IDEA_REVIEW_ATTEMPTS} 轮均未达标 "
                    f"(final_score={score:.2f}), 暂停优化等待人工介入"
                )
            prop_state["idea_review_passed"] = False
            prop_state["idea_review_blocked"] = True
            self._set_proposal_state(proposal_id, prop_state)
            return {
                "success": False,
                "error": (
                    f"研究设想评审 {MAX_IDEA_REVIEW_ATTEMPTS} 轮均未达标"
                    f"（最高分 {score:.2f} < {IDEA_REVIEW_THRESHOLD}），"
                    f"暂停优化等待人工介入"
                ),
                "idea_review_score": score,
                "attempts": attempt,
                "passed": False,
                "blocked": True,
            }

    # 理论上不会到达
    return {"success": False, "error": "研究设想评审异常退出"}


def _parse_idea_review_score(report_text: str) -> tuple:
    """从评审报告中解析综合评分和问题摘要。

    返回 (score: float, issues: str)。
    """
    import re

    score = 0.0
    # 匹配 "综合评分：0.73" 或 "综合评分: 0.73"
    m = re.search(r"综合评分[：:]\s*([0-9]\.?\d*)", report_text)
    if m:
        try:
            score = float(m.group(1))
        except ValueError:
            pass

    # 如果没有综合评分，尝试取所有维度分数的均值
    if score == 0.0:
        dim_scores = re.findall(r"[：:]\s*([0-9]\.?\d*)", report_text)
        valid = [float(s) for s in dim_scores if 0 <= float(s) <= 1]
        if valid:
            score = sum(valid) / len(valid)

    # 提取问题摘要（取报告前 500 字作为 issues）
    issues = report_text[:500]

    return score, issues


def _run_update_vision_step(self, proposal_id: str, job: Dict[str, Any]) -> Dict[str, Any]:
    """v6.8.0: 根据最终申请书更新研究设想（proposal-brief）。"""
    prop_dir = self._find_proposal_dir(proposal_id)
    if not prop_dir:
        return {"success": False, "error": "proposal 目录不存在"}

    proposal_path = prop_dir / "04_proposal" / "proposal-draft.md"
    if not proposal_path.exists():
        return {"success": False, "error": "申请书不存在"}

    brief_path = prop_dir / "00_proposal-brief.md"
    draft = proposal_path.read_text(encoding="utf-8")[:8000]

    prompt = (
        f"请根据以下申请书内容，更新课题设想/研究概要（{brief_path}）。\n\n"
        f"要求：\n"
        f"1. 用凝练的叙述风格概括研究问题、科学意义、核心创新、预期贡献\n"
        f"2. 不要罗列细节，突出研究思路主线\n"
        f"3. 输出为 markdown，包含 # 标题 和 > 项目类型等元信息\n"
        f"4. 直接写入文件 {brief_path}\n\n"
        f"【申请书内容】\n{draft}\n"
    )
    # v6.8.39: 超时 300s→600s，与 v6.8.37 references/critic 修复策略一致。
    # writer 长内容生成（研究设想/方法学手册）在 300s 内常超时，
    # key-transient r1 update_method_manual 已实测超时(300s)，重试耗尽会卡住轮次。
    result = self._run_hermes("writer", prompt, timeout=600)
    if not result.get("success"):
        return {"success": False, "error": result.get("error", "更新研究设想失败")}
    return {"success": True, "brief_path": str(brief_path)}


def _run_update_method_manual_step(self, proposal_id: str, job: Dict[str, Any]) -> Dict[str, Any]:
    """v6.8.0: 根据申请书更新方法学手册，在方法层面补充细节。"""
    prop_dir = self._find_proposal_dir(proposal_id)
    if not prop_dir:
        return {"success": False, "error": "proposal 目录不存在"}

    proposal_path = prop_dir / "04_proposal" / "proposal-draft.md"
    if not proposal_path.exists():
        return {"success": False, "error": "申请书不存在"}

    method_dir = prop_dir / "03_method"
    method_dir.mkdir(parents=True, exist_ok=True)
    manual_path = method_dir / "method-manual.md"

    # 优先读取 scheme 模块的 writer 输出，若不存在则读完整 draft
    scheme_path = prop_dir / "04_proposal" / "sections" / "scheme.md"
    if scheme_path.exists():
        method_source = scheme_path.read_text(encoding="utf-8")[:8000]
    else:
        method_source = proposal_path.read_text(encoding="utf-8")[:8000]

    prompt = (
        f"请根据以下申请书的研究方案部分，撰写方法学手册（{manual_path}）。\n\n"
        f"要求：\n"
        f"1. 在申请书思路基础上，补充具体方法细节：算法/实验步骤、关键参数、验证方式\n"
        f"2. 说明潜在风险和替代方案\n"
        f"3. 方法学手册是方法层面的补充文档，不要重复申请书的思路性叙述\n"
        f"4. 直接写入文件 {manual_path}\n\n"
        f"【研究方案内容】\n{method_source}\n"
    )
    # v6.8.39: 超时 300s→600s，与 v6.8.37 references/critic 修复策略一致。
    # key-transient r1 该步骤已实测超时(300s)，重试耗尽会卡住轮次（轮次链末端）。
    result = self._run_hermes("writer", prompt, timeout=600)
    if not result.get("success"):
        return {"success": False, "error": result.get("error", "更新方法学手册失败")}
    return {"success": True, "manual_path": str(manual_path)}


def _run_monitor_step(self, proposal_id: str, job: Dict[str, Any]) -> Dict[str, Any]:
    """执行 monitor（全局监察）步骤：评分、奖惩、达标判定、流转。

    v6.7.6: monitor 作为每轮 writer-critic 之后的收尾步骤，独立评估质量，
    更新 agent 分数，检测负反馈，最终决定是否达标并移入 pending_review。
    """
    if AdversarialGovernance is None:
        if _log:
            _log.warning(f"[{proposal_id}] adversarial_governance 未加载，monitor 跳过")
        # v6.8.27 修复: round_num 在此处尚未定义（定义在 L1228），
        # 从 job 中直接提取，避免降级路径 NameError
        round_num_fallback = job.get("round", 0)
        prop_state = self._get_proposal_state(proposal_id)
        if prop_state:
            prop_state["optimization_rounds"] = max(
                prop_state.get("optimization_rounds", 0), round_num_fallback
            )
            prop_state["last_monitor_assessment"] = "adversarial_governance 未加载，monitor 跳过"
            prop_state["updated_at"] = now_utc()
            self._set_proposal_state(proposal_id, prop_state)
        return {"success": True, "skipped": True, "reason": "adversarial_governance 未加载"}

    prop_dir = self._find_proposal_dir(proposal_id)
    if not prop_dir:
        return {"success": False, "error": "proposal 目录不存在"}

    prop_state = self._get_proposal_state(proposal_id)
    if not prop_state:
        return {"success": False, "error": "proposal 状态不存在"}

    project_type = prop_state.get("project_type", "general")
    round_num = job["round"]
    section_key = job["section_key"]
    from proposal_sections import PROPOSAL_SECTIONS
    section = next((s for s in PROPOSAL_SECTIONS if s["key"] == section_key), None)
    section_name = section.get("cn", section_key) if section else section_key

    score_after = prop_state.get("last_score", 0.0)
    dim_scores = prop_state.get("last_dim_scores", {})

    # 找上一轮的 score 作为 score_before
    score_before = 0.0
    score_history = prop_state.get("score_history", [])
    for h in reversed(score_history[:-1]):
        if h.get("round") < round_num:
            score_before = h.get("score", 0.0)
            break

    # 找 writer 修改前的备份文件作为 prev_draft
    prev_draft_path = prop_dir / "04_proposal" / f"proposal-draft-r{round_num - 1}.md"
    if not prev_draft_path.exists():
        prev_draft_path = None

    ag = AdversarialGovernance()
    monitor_result = ag.run_monitor_step(
        proposal_id=proposal_id,
        prop_dir=prop_dir,
        project_type=project_type,
        round_num=round_num,
        section_key=section_key,
        section_name=section_name,
        score_before=score_before,
        score_after=score_after,
        dim_scores=dim_scores,
        prev_draft_path=prev_draft_path,
    )

    if not monitor_result.get("success"):
        return {
            "success": False,
            "error": monitor_result.get("error", "monitor 调用失败"),
            "monitor_result": monitor_result,
        }

    deltas = ag.apply_monitor_result(
        proposal_id=proposal_id,
        round_num=round_num,
        section_key=section_key,
        score_before=score_before,
        score_after=score_after,
        dim_scores=dim_scores,
        monitor_result=monitor_result,
        proposal_state=prop_state,
    )

    prop_state = ag.record_monitor_history(
        proposal_state=prop_state,
        round_num=round_num,
        section_key=section_key,
        score_before=score_before,
        score_after=score_after,
        monitor_result=monitor_result,
        deltas=deltas,
    )

    # 本轮完整闭环结束，推进轮次（负反馈告警时除外）
    if not prop_state.get("negative_feedback_alert"):
        old_rounds = prop_state.get("optimization_rounds", 0)
        prop_state["optimization_rounds"] = max(old_rounds, round_num)
        # v6.8.21: 清理旧轮次 job
        if prop_state["optimization_rounds"] > old_rounds:
            from .utils import archive_old_round_jobs
            archive_old_round_jobs(proposal_id, prop_state["optimization_rounds"])

    # 写入 monitor 简要摘要到 proposal 状态
    prop_state["last_monitor_at"] = now_utc()
    prop_state["last_monitor_score"] = monitor_result.get("monitor_independent_score", score_after)
    prop_state["last_monitor_assessment"] = monitor_result.get("overall_assessment", "")[:300]
    self._set_proposal_state(proposal_id, prop_state)

    # v6.9.0 R3: 连续两轮下降且距最佳超过幅度 → 自动回退最佳轮次草稿
    # （先于 _check_done：若下降路径晋级待审，人工看到的也是最佳版本）
    try:
        from .utils import perform_auto_rollback, should_auto_rollback

        _rb_plan = should_auto_rollback(prop_state)
        if _rb_plan:
            _rb = perform_auto_rollback(proposal_id, prop_state, _rb_plan)
            if _rb.get("success"):
                self._set_proposal_state(proposal_id, prop_state)
                if _log:
                    _log.info(
                        f"[{proposal_id}] 连续下降自动回退至 R{_rb_plan['best_round']} "
                        f"（最佳 {_rb_plan['best_score']:.2f}，当前 {_rb_plan['current']:.2f}）"
                    )
            elif _log:
                _log.info(
                    f"[{proposal_id}] 触发回退条件但未执行：{_rb.get('error')}"
                )
    except Exception as _rb_exc:  # pragma: no cover
        if _log:
            _log.warning(f"[{proposal_id}] 自动回退检查失败: {_rb_exc}")

    # 负反馈告警：不流转，等待人工介入
    if prop_state.get("negative_feedback_alert"):
        reasons = prop_state.get("negative_feedback_reasons", [])
        # v6.9.0 R2: 补戳触发时间（遗留数据无时间戳，供 24h 冷却自动清除判定）
        if not prop_state.get("negative_feedback_at"):
            prop_state["negative_feedback_at"] = now_utc()
            self._set_proposal_state(proposal_id, prop_state)
        if _log:
            _log.warning(
                f"[{proposal_id}] 触发负反馈告警: {', '.join(reasons)}; "
                f"暂停自动流转，等待人工清除"
            )
        return {
            "success": True,
            "negative_feedback_alert": True,
            "reasons": reasons,
            "writer_delta": deltas.get("writer_delta"),
            "critic_delta": deltas.get("critic_delta"),
            "monitor_score": monitor_result.get("monitor_independent_score"),
        }

    # 未触发负反馈：检查是否达标并流转
    threshold = self._get_quality_threshold(project_type)
    done_result = self._check_done(proposal_id, threshold)
    if done_result["done"]:
        transition_result = self.transition(
            proposal_id, "pending_review", reason=done_result["reason"]
        )
        # v6.8.3: 逃生阀触发的质量警告写入 proposal_state
        quality_warning = done_result.get("quality_warning")
        if quality_warning:
            prop_state = self._get_proposal_state(proposal_id)
            if prop_state:
                prop_state["quality_warning"] = quality_warning
                self._set_proposal_state(proposal_id, prop_state)
                if _log:
                    _log.warning(f"[{proposal_id}] {quality_warning}")
        # v6.9.0 R1: 晋级待审自动生成验收决策包（best-effort，失败不影响晋级）
        try:
            from review_dossier import generate_review_dossier

            _dossier = generate_review_dossier(proposal_id)
            if _dossier.get("success") and _log:
                _log.info(
                    f"[{proposal_id}] 验收决策包已生成："
                    f"预审 {_dossier['pre_review_verdict']}"
                )
        except Exception as _dos_exc:  # pragma: no cover
            if _log:
                _log.warning(f"[{proposal_id}] 决策包生成失败（不影响晋级）: {_dos_exc}")
        return {
            "success": True,
            "done": True,
            "reason": done_result["reason"],
            "quality_warning": quality_warning,
            "transition": transition_result,
            "writer_delta": deltas.get("writer_delta"),
            "critic_delta": deltas.get("critic_delta"),
            "monitor_score": monitor_result.get("monitor_independent_score"),
        }

    # v6.8.26: 结构性缺陷检测——content/scheme 文件级重复或模块空置
    # 检测到时设置 idea_review_required 标志，下一轮前置 idea_review job
    structural_defect = _detect_structural_defect(prop_dir)
    if structural_defect:
        prop_state = self._get_proposal_state(proposal_id) or {}
        prop_state["idea_review_required"] = True
        prop_state["idea_review_required_reason"] = structural_defect
        self._set_proposal_state(proposal_id, prop_state)
        if _log:
            _log.warning(
                f"[{proposal_id}] 检测到结构性缺陷：{structural_defect}，"
                f"下一轮将重新触发研究设想评审"
            )

    return {
        "success": True,
        "done": False,
        "reason": done_result.get("reason", "未达标"),
        "writer_delta": deltas.get("writer_delta"),
        "critic_delta": deltas.get("critic_delta"),
        "monitor_score": monitor_result.get("monitor_independent_score"),
        "structural_defect": structural_defect or None,
    }


def _detect_structural_defect(prop_dir: Path) -> str:
    """v6.8.26: 检测申请书结构性缺陷——content/scheme 文件级重复或模块空置。

    返回缺陷描述字符串（无缺陷返回空字符串）。
    """
    sections_dir = prop_dir / "04_proposal" / "sections"
    if not sections_dir.exists():
        return ""

    content_path = sections_dir / "content.md"
    scheme_path = sections_dir / "scheme.md"

    # 检测模块空置
    for name, path in [("研究内容", content_path), ("研究方案", scheme_path)]:
        if path.exists() and path.stat().st_size < 50:
            return f"{name}模块空置（文件不足50字节）"

    if not content_path.exists() or not scheme_path.exists():
        return ""

    content_text = content_path.read_text(encoding="utf-8")
    scheme_text = scheme_path.read_text(encoding="utf-8")

    # 检测文件级重复：取 content 前 200 字符，检查是否在 scheme 中出现
    if len(content_text) > 200:
        sample = content_text[:200].strip()
        if sample and sample in scheme_text:
            return "研究内容与研究方案存在文件级重复（前200字符完全匹配）"

    # 反向检测
    if len(scheme_text) > 200:
        sample = scheme_text[:200].strip()
        if sample and sample in content_text:
            return "研究方案与研究内容存在文件级重复（前200字符完全匹配）"

    return ""

def execute_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
    """执行一个 checkpoint job（不获取锁，调用方负责锁）。"""
    import time

    proposal_id = job["proposal_id"]
    step = job["step"]
    round_num = job.get("round", 0)

    # v6.7.12: 保持与 optimize.py 相同的日志格式，供 profile_health 统计
    step_verb = {
        STEP_CRITIC: "评审",
        STEP_WRITER: "优化",
        STEP_RESEARCHER: "定向检索",
        STEP_MONITOR: "监察",
        STEP_UPDATE_VISION: "更新研究设想",
        STEP_UPDATE_METHOD_MANUAL: "更新方法学手册",
        STEP_IDEA_REVIEW: "研究设想评审",
    }.get(step, step)
    if _log:
        _log.info(f"[{proposal_id}] 对抗轮 {round_num}: {step} {step_verb}")

    self._update_job(proposal_id, job, JOB_STATUS_RUNNING)

    t0 = time.time()
    try:
        if step == STEP_CRITIC:
            result = self._run_critic_step(proposal_id, job)
        elif step == STEP_RESEARCHER:
            result = self._run_researcher_step(proposal_id, job)
        elif step == STEP_GAP_IDENTIFY:
            result = self._run_gap_identify_step(proposal_id, job)
        elif step == STEP_LIT_SEARCH:
            result = self._run_lit_search_step(proposal_id, job)
        elif step == STEP_LIT_READ:
            result = self._run_lit_read_step(proposal_id, job)
        elif step == STEP_LIT_NOTE:
            result = self._run_lit_note_step(proposal_id, job)
        elif step == STEP_WRITER:
            result = self._run_writer_step(proposal_id, job)
        elif step == STEP_MONITOR:
            result = self._run_monitor_step(proposal_id, job)
        elif step == STEP_UPDATE_VISION:
            result = self._run_update_vision_step(proposal_id, job)
        elif step == STEP_UPDATE_METHOD_MANUAL:
            result = self._run_update_method_manual_step(proposal_id, job)
        elif step == STEP_IDEA_REVIEW:
            result = self._run_idea_review_step(proposal_id, job)
        else:
            result = {"success": False, "error": f"未知步骤 {step}"}
    except Exception as e:
        result = {"success": False, "error": str(e)}
    elapsed = round(time.time() - t0, 2)

    if result.get("success"):
        self._update_job(proposal_id, job, JOB_STATUS_DONE)
        # monitor 是每轮完整闭环的收尾步骤；只有 monitor 成功后，
        # 才推进 optimization_rounds 并生成下一轮 checkpoint。
        if step == STEP_MONITOR and not result.get("negative_feedback_alert"):
            self.sync_checkpoint(proposal_id)
    else:
        self._update_job(proposal_id, job, JOB_STATUS_FAILED, result.get("error", ""))

    if _log:
        _log.info(
            f"[{proposal_id}] 对抗轮 {round_num}: {step} 完成 "
            f"success={result.get('success')} elapsed={elapsed}s"
        )
    return result

def execute_next_job(self, proposal_id: str) -> Dict[str, Any]:
    """worker 入口：加锁、挑选并执行下一个 job。"""
    prop_state = self._get_proposal_state(proposal_id)
    if not prop_state:
        return {"success": False, "error": "proposal 未注册"}
    if prop_state.get("status") != "optimizing":
        return {"success": False, "error": f"proposal 不在优化中（当前: {prop_state['status']}）"}

    # 先补齐 checkpoint
    self.sync_checkpoint(proposal_id)

    with file_lock(f"proposal-{proposal_id}"):
        job = self.pick_next_job(proposal_id)
        if not job:
            return {"success": True, "reason": "无待执行 job", "executed": False}
        result = self.execute_job(job)
        result["executed"] = True
        result["job_id"] = job["job_id"]
        return result
