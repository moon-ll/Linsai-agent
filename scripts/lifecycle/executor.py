#!/usr/bin/env python3
"""生命周期 cron 框架单步执行器。"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import file_lock, now_utc

from .constants import (
    JOB_STATUS_DONE,
    JOB_STATUS_FAILED,
    JOB_STATUS_PENDING,
    JOB_STATUS_RUNNING,
    STALE_RUNNING_SECONDS,
    STEP_CRITIC,
    STEP_GAP_IDENTIFY,
    STEP_LIT_NOTE,
    STEP_LIT_READ,
    STEP_LIT_SEARCH,
    STEP_MONITOR,
    STEP_RESEARCHER,
    STEP_UPDATE_METHOD_MANUAL,
    STEP_UPDATE_VISION,
    STEP_WRITER,
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
        "dim_scores": self._extract_dimension_scores(file_result),
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
    from proposal_sections import PROPOSAL_SECTIONS
    section = next((s for s in PROPOSAL_SECTIONS if s["key"] == section_key), None)
    focus_section = section
    is_full_review = section_key == "full_review"

    result = self._run_critic(
        proposal_id, prop_dir, project_type, round_num, 900,
        focus_section=focus_section, is_full_review=is_full_review,
    )
    if not result.get("success"):
        return {"success": False, "error": result.get("error", "critic 失败")}

    # 等待报告落盘
    report_path = prop_dir / "05_review" / f"critic-round-{round_num}.md"
    if not (report_path.exists() and report_path.stat().st_size > 100):
        self._wait_for_critic_report(report_path, timeout=30)

    # 解析报告，决定是否需要 researcher
    report = self._read_critic_report(prop_dir, round_num)
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
        f"4. 输出严格 JSON，格式如下：\n"
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
        if text.startswith("```"):
            lines = text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        data = json.loads(text)
        if not isinstance(data, dict) or "gaps" not in data:
            return {"success": False, "error": "返回 JSON 缺少 gaps 字段"}

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

    agent_prompt = (
        f"你是一位专业研究助手（Researcher）。请针对课题「{proposal_id}」的"
        f"「{section_name}」部分，检索以下关键词的最新论文。\n\n"
        f"【检索关键词】\n{keyword_str}\n\n"
        f"请执行：\n"
        f"1. 使用 web_search 工具逐一检索每个关键词\n"
        f"2. 对每篇论文，提取完整信息：arxiv_id、标题、作者、年份、TL;DR\n"
        f"3. 优先选择 2024-2026 年的最新论文\n"
        f"4. 输出格式：每行一个结果，用 | 分隔，格式：\n"
        f"   - arxiv_id | 标题 | 作者 | 年份 | 相关性评分(0-1) | 一句话摘要 | 来源：联网检索\n"
    )

    try:
        agent_result = _run_hermes_agent("researcher", agent_prompt, timeout=360)
        if agent_result.get("success"):
            agent_success = True
            output = agent_result.get("output", "")
            # 解析 agent 输出中的论文列表
            from literature_service import LiteratureService
            svc = LiteratureService()
            papers = svc._parse_researcher_output(output)
            if _log:
                _log.info(
                    f"[{proposal_id}] lit_search agent loop 成功，"
                    f"解析到 {len(papers)} 篇论文"
                )
    except Exception as e:
        if _log:
            _log.warning(f"[{proposal_id}] lit_search agent loop 异常: {e}")

    # 步骤2：如果 agent loop 失败或未获取到论文，降级为 LiteratureService
    if not agent_success or not papers:
        if not agent_success and _log:
            _log.warning(
                f"[{proposal_id}] lit_search agent loop 失败，降级 LiteratureService"
            )
        try:
            from literature_service import LiteratureService
            svc = LiteratureService()
            papers = svc.search(
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

    # 步骤3：回写 researcher profile 记忆
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
    return {"success": bool(papers), "result_path": str(result_path), "method": method_tag}


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
            f"2. 输出格式：\n"
            f"   ## 核心结论\n"
            f"   ## 方法与创新\n"
            f"   ## 与课题关联\n"
            f"   ## 关键图表/数据\n"
            f"   ## 局限性\n"
        )
        try:
            agent_result = _run_hermes_agent("researcher", agent_prompt, timeout=240)
            if agent_result.get("success"):
                agent_success = True
                output = agent_result.get("output", "")
                notes.append(f"## {aid}\n\n{output}\n")
                read_count += 1
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
        _log.warning(f"[{proposal_id}] lit_note 跳过: 无检索报告可导入")
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

    writer_result = self._run_writer_optimize(
        proposal_id, prop_dir, project_type,
        critic_result={"output": report["output"]},
        timeout=900,
        weakest_dim=weakest_dim,
        dim_scores=dim_scores,
        focus_section=focus_section,
        is_full_review=is_full_review,
        lit_supplement=lit_supplement,
    )
    if not writer_result.get("success"):
        return {"success": False, "error": writer_result.get("error", "writer 失败")}

    # 重新读取报告计算分数（writer 不应修改 critic 报告）
    report = self._read_critic_report(prop_dir, round_num)
    score_after = report["score"]
    dim_scores = report["dim_scores"]
    weakest_dim = self._get_weakest_dimension(dim_scores)
    issues = report["issues"]

    min_score = threshold.get("min_overall_score", 0.80)
    weak_dims = [k for k, floor in self.DIMENSION_FLOOR.items() if k in dim_scores and dim_scores[k] < floor]
    section_passed = score_after >= min_score and len(weak_dims) == 0

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
    }

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
    result = self._run_hermes("writer", prompt, timeout=300)
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
    result = self._run_hermes("writer", prompt, timeout=300)
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
        # 降级处理：虽未启用监察模块，仍推进轮次，避免链路僵死
        prop_state = self._get_proposal_state(proposal_id)
        if prop_state:
            prop_state["optimization_rounds"] = max(
                prop_state.get("optimization_rounds", 0), round_num
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
        prop_state["optimization_rounds"] = max(
            prop_state.get("optimization_rounds", 0), round_num
        )

    # 写入 monitor 简要摘要到 proposal 状态
    prop_state["last_monitor_at"] = now_utc()
    prop_state["last_monitor_score"] = monitor_result.get("monitor_independent_score", score_after)
    prop_state["last_monitor_assessment"] = monitor_result.get("overall_assessment", "")[:300]
    self._set_proposal_state(proposal_id, prop_state)

    # 负反馈告警：不流转，等待人工介入
    if prop_state.get("negative_feedback_alert"):
        reasons = prop_state.get("negative_feedback_reasons", [])
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
        return {
            "success": True,
            "done": True,
            "reason": done_result["reason"],
            "transition": transition_result,
            "writer_delta": deltas.get("writer_delta"),
            "critic_delta": deltas.get("critic_delta"),
            "monitor_score": monitor_result.get("monitor_independent_score"),
        }

    return {
        "success": True,
        "done": False,
        "reason": done_result.get("reason", "未达标"),
        "writer_delta": deltas.get("writer_delta"),
        "critic_delta": deltas.get("critic_delta"),
        "monitor_score": monitor_result.get("monitor_independent_score"),
    }

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
