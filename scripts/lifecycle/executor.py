#!/usr/bin/env python3
"""生命周期 cron 框架单步执行器。"""

from __future__ import annotations

import json
import re
import shutil
import difflib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import file_lock, now_utc

# v7.2.2: 提升 hermes_memory 关键符号到模块级（消除函数内 import 引发的
# UnboundLocalError）。原 4 处函数内 `from hermes_memory import _run_hermes_agent,
# _write_memory` 在 except 块中引用 `_write_memory` 时会触发
# "cannot access local variable '_write_memory' where it is not associated
# with a value"。fail-open：导入失败降级为 None，与 llm_router /
# adversarial_governance 守卫风格一致。
try:
    from hermes_memory import _run_hermes_agent, _write_memory  # noqa: F401
except Exception:  # pragma: no cover - 防御导入错误
    _run_hermes_agent = None  # type: ignore[assignment]
    _write_memory = None  # type: ignore[assignment]

from .constants import (
    IDEA_REVIEW_THRESHOLD,
    JOB_STATUS_DONE,
    JOB_STATUS_FAILED,
    JOB_STATUS_PENDING,
    JOB_STATUS_RUNNING,
    MANUAL_MIN_BYTES,
    MANUAL_READY_LEVEL,
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


def _step_hermes_timeout(job: Optional[Dict[str, Any]], base: int) -> int:
    """v7.3.45: 按尝试次数梯度放宽 researcher 步骤超时。

    11 月账本实测：researcher agent loop 成功时长 p50=144s / p90=284s /
    p99=372s / max=531s，而 gap_identify(300s)/lit_search(360s)/
    lit_read(600s) 基线正卡在成功分布尾部——5 天 67 次硬超时全部落在
    300/360/600 整数线上，每次浪费整段超时时长后再整步重跑。

    策略：基线抬到覆盖 p90，重试时每次 +120s（覆盖 p99-max 尾部）。
    真僵死仍受 stale-running 守卫（1800s）与熔断器约束。attempts 语义
    （_update_job 仅在失败时递增）：执行时 job 上即为"此前已失败次数"。
    """
    try:
        prior_fails = int((job or {}).get("attempts", 0) or 0)
    except (TypeError, ValueError):
        prior_fails = 0
    return min(base + max(prior_fails, 0) * 120, base + 240)


# v7.2.41 BUG-8 修复：口径感知的维度完备性期望集。
# 旧实现对正文章节轮用 DIMENSION_FLOOR 全集（含 completeness）作期望，
# 而 completeness 是 references 专轮（2 维口径 rigor/completeness）的
# 专属维度——正文轮 critic 按 4 维（innovation/feasibility/rigor/
# expression）打分，completeness 永不产出 → 正文轮 dims_partial 恒为
# True（实测全库 148/148 = 100%），把 completion.py 六道质量门
# （收敛/次优平台/验收晋级/评审团/质量下降）与看板 4 维全部封死。
SECTION_DIM_KEYS = ("innovation", "feasibility", "rigor", "expression")
REFERENCES_DIM_KEYS = ("rigor", "completeness")
# v7.3.0: 方法手册模块 2 维专用口径——readiness（就绪度：八要素覆盖 +
# L0-L4 分级）与 rigor（参数溯源真实/数值可复算/与口径表一致）。
# 与 references 的 2 维口径同构：手册不是申请书正文，创新性/可行性/表达
# 质量不适用，锚点语体对比也不适用（手册是操作文档）。
MANUAL_DIM_KEYS = ("readiness", "rigor")


def caliber_dim_key(section_key: str) -> str:
    """把 step 的伪章节 section_key 归一到真实评分口径。

    v7.2.42 BUG-9：monitor job 的 section_key 是伪章节 "monitor"
    （不在 PROPOSAL_SECTIONS 中），但其 depends_on 恒为 references-writer
    （controller.py:415 建轮不变量），评判对象实为 references 专轮。
    不归一时，口径感知判定会按章节 4 维期望去比对 references 的 2 维
    报告 → 恒判残缺 → agent 奖惩 100% 被静默跳过（实测全库 20/20）。
    """
    if section_key == STEP_MONITOR:
        return "references"
    return section_key


def expected_dim_keys(section_key: str) -> tuple:
    """按评分口径返回该轮期望的维度集。

    v7.2.41：口径自洽——章节轮与 full_review 轮走 4 维加权口径，
    references 轮走 2 维专用口径（rigor/completeness）。
    v7.2.42：入口先经 caliber_dim_key 归一，monitor 落到 references 口径。
    v7.3.0：method_manual 轮走手册 2 维专用口径（readiness/rigor）。
    """
    _caliber = caliber_dim_key(section_key)
    if _caliber == "references":
        return REFERENCES_DIM_KEYS
    if _caliber == "method_manual":
        return MANUAL_DIM_KEYS
    return SECTION_DIM_KEYS


def judge_dims_partial(section_key: str, dim_scores: Dict[str, Any]) -> tuple:
    """判定该轮维度是否残缺，返回 (dims_partial, dims_present, missing)。

    v7.2.41：口径感知判定的唯一实现入口，score_history 入史
    （_run_writer_step）与 agent 奖惩守卫（_run_monitor_step）共用，
    避免两处口径漂移。
    """
    expected = set(expected_dim_keys(section_key))
    present = set(dim_scores or {})
    missing = expected - present
    return bool(missing), sorted(present), sorted(missing)


def _repair_json_inner_quotes(text: str) -> str:
    """v6.10.6: 修复字符串内未转义 ASCII 引号导致的 JSON 非法。

    启发式状态机：处于字符串内时遇到的 `"`，若其后首个非空白字符不是
    JSON 结构字符（: , } ]）也不是文本末尾，则判定为内容引号，转义为
    `\\"`。典型场景：LLM 在中文 claim 里写 `论证"光源—样品"五环`
    （应为全角引号却用了 ASCII 引号），使整段 JSON 解析失败。
    """
    out: list = []
    in_string = False
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if not in_string:
            if ch == '"':
                in_string = True
            out.append(ch)
        elif ch == "\\":
            out.append(ch)
            if i + 1 < n:
                out.append(text[i + 1])
                i += 1
        elif ch == '"':
            j = i + 1
            while j < n and text[j] in " \t\r\n":
                j += 1
            if j >= n or text[j] in ":,}]":
                in_string = False
                out.append(ch)
            else:
                out.append('\\"')
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def _extract_gaps_json(text: str) -> Optional[Dict[str, Any]]:
    """v6.10.55: 从 LLM 输出中提取 {"gaps": [...]} 载荷（纯函数，可单测）。

    解析链：去 markdown 围栏 → 直接 json.loads → 花括号配平提取 →
    引号修复兜底（_repair_json_inner_quotes）。任何一步成功即返回
    含 "gaps" 键的 dict；全部失败返回 None。
    """
    if not text or not text.strip():
        return None
    t = text.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        t = "\n".join(lines).strip()

    def _balanced_parse(s: str) -> Optional[Dict[str, Any]]:
        for start in range(len(s)):
            if s[start] != "{":
                continue
            depth = 0
            for end in range(start, len(s)):
                if s[end] == "{":
                    depth += 1
                elif s[end] == "}":
                    depth -= 1
                    if depth == 0:
                        # v6.10.55: 仅在深度归零（完整对象闭合）时尝试解析；
                        # 失败则继续扫描后续起点（旧实现 break 早停于首个
                        # 内层 `}`，嵌套 JSON 的配平提取形同虚设）
                        try:
                            parsed = json.loads(s[start:end + 1])
                            if isinstance(parsed, dict) and "gaps" in parsed:
                                return parsed
                        except json.JSONDecodeError:
                            pass
                        break
        return None

    # 1) 直接解析
    try:
        data = json.loads(t)
        if isinstance(data, dict) and "gaps" in data:
            return data
    except json.JSONDecodeError:
        pass
    # 2) 花括号配平提取（JSON 嵌在自然语言中的场景）
    found = _balanced_parse(t)
    if found:
        return found
    # 3) 引号修复兜底（中文 claim 内嵌 ASCII 引号场景，v6.10.6）
    repaired = _repair_json_inner_quotes(t)
    if repaired != t:
        try:
            data = json.loads(repaired)
            if isinstance(data, dict) and "gaps" in data:
                return data
        except json.JSONDecodeError:
            pass
        found = _balanced_parse(repaired)
        if found:
            return found
    return None


# v6.10.55: lit_read 深读上限（分诊后仍保留的重读数）
_LIT_READ_CAP = 3


def _valid_brief_text(text: str) -> bool:
    """v6.10.55: update_vision 直调产物的结构校验（纯函数，可单测）。

    brief 契约（原 prompt 要求）：markdown、含 # 标题（或 frontmatter）、
    实质内容 ≥200 字符；不满足则视为无效，回退 writer agent loop。
    """
    t = (text or "").strip()
    if len(t) < 200:
        return False
    return t.startswith(("#", "---")) or "\n# " in t


def _parse_lit_report_papers(text: str) -> List[Dict[str, str]]:
    """v6.10.55: 解析 lit-gap 报告「## 检索结果」段的论文条目（纯函数）。

    条目格式（lit_search 落盘口径）：
        - {arxiv_id} | {title} | {authors} | {year} | {score} | {tldr} | 来源：{x}
    仅解析主检索段（多源补充段格式不同，不参与分诊）；格式漂移返回空列表，
    由调用方回退原序逻辑。
    """
    papers: List[Dict[str, str]] = []
    m = re.search(r"## 检索结果\n(.*?)(?:\n## |\Z)", text or "", re.S)
    if not m:
        return papers
    for line in m.group(1).splitlines():
        line = line.strip()
        mid = re.match(r"-\s*(\d{4}\.\d{4,5})\s*\|", line)
        if not mid:
            continue
        parts = [x.strip() for x in line[2:].split("|")]
        papers.append({
            "arxiv_id": mid.group(1),
            "title": parts[1] if len(parts) > 1 else "",
            "tldr": parts[5] if len(parts) > 5 else "",
        })
    return papers


def _rank_lit_read_ids(
    papers: List[Dict[str, str]], keywords_text: str, cap: int = _LIT_READ_CAP
) -> List[str]:
    """v6.10.55: 分诊排序——按检索关键词在 标题+tldr 中的命中数降序（纯函数）。

    命中数相同的保持报告原序（Python 排序稳定）；全部 0 命中时排序退化
    为原序（分诊上限仍然生效）。返回去重后的 arxiv_id 列表（≤cap）。
    """
    kws = [k.strip().lower() for k in re.split(r"[、,;，；]", keywords_text or "")
           if k.strip()]

    def _score(p: Dict[str, str]) -> int:
        hay = f"{p.get('title', '')} {p.get('tldr', '')}".lower()
        return sum(1 for k in kws if k and k in hay)

    ranked = sorted(papers, key=lambda p: -_score(p))
    out: List[str] = []
    for p in ranked:
        aid = p.get("arxiv_id", "")
        if aid and aid not in out:
            out.append(aid)
        if len(out) >= cap:
            break
    return out


# v6.9.54: 写入门卫 + 质量门——结构不变量从 prompt 约定升级为确定性强制
# v6.9.55: 质量核心重构——拦截判据从字数（症状）改为冗余/无关（病因），
# 字数降级为上下文信号：实质性长文（无质量缺陷）放行。
try:
    from proposal_lifecycle.section_hygiene import (
        quality_gate,
        guard_written_artifacts,
        section_char_count,
    )
except Exception:  # 守卫模块缺失时 fail-open（不阻塞主管线）
    quality_gate = None
    guard_written_artifacts = None
    section_char_count = None


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

def _read_critic_report(self, prop_dir: Path, round_num: int,
                        section_key: Optional[str] = None) -> Dict[str, Any]:
    """读取指定轮次的 critic 报告并解析分数。

    v6.10.26: section 感知读盘——优先读 `critic-round-{n}-{section}.md`
    （评审团/新写盘约定的后缀报告，与轮内其他 section 隔离），后缀文件
    不存在时回退裸路径 `critic-round-{n}.md`（历史报告兼容；裸文件被
    references 报告占用时，章节轮会误读 2 维伪分——旧缺陷，见
    proposal_lifecycle.optimize._critic_report_path docstring）。
    """
    review_dir = prop_dir / "05_review"
    report_path = None
    if section_key:
        cand = review_dir / f"critic-round-{round_num}-{section_key}.md"
        if cand.exists():
            report_path = cand
    if report_path is None:
        report_path = review_dir / f"critic-round-{round_num}.md"
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

def _salvage_critic_report(self, report_path: Path, job: Dict[str, Any]) -> bool:
    """v7.3.75: 评审超时假失败捞回。

    背景：critic 在墙钟上限被终止（key-transient 实测 elapsed=1501.27s），
    但 agent 在超时前已把完整报告写盘（含 `## 评分` 块）。直接按
    success=False 结算会触发整轮重跑（attempt 2/3），白烧约 25 分钟，
    且下轮报告可能覆盖本轮有效结论。
    只在「报告于本次开工之后写入」且「含可解析评分块」时捞回，
    避免把上一次尝试的旧报告误当本轮产物。
    """
    try:
        if not (report_path.exists() and report_path.stat().st_size > 100):
            return False
        started = job.get("_run_started_at") or job.get("started_at") or ""
        if not started:
            return False
        mtime = datetime.fromtimestamp(report_path.stat().st_mtime, timezone.utc)
        if mtime.strftime("%Y-%m-%dT%H:%M:%SZ") < started:
            return False
        text = report_path.read_text(encoding="utf-8", errors="ignore")
        return "## 评分" in text and "综合评分" in text
    except Exception:
        return False

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

    # v7.2.13: 评审前零 LLM 口径校验——params.json 存在时把冲突清单
    # 注入 critic prompt（发现正文数值与口径表不符 → 按 consistency_check
    # 红线直接计 critical，无需 critic 自行跨章比对数值）
    _params_check_text = ""
    try:
        from .params_registry import load_params, check_consistency, format_params_block
        _pdata = load_params(prop_dir)
        if _pdata:
            _pchk = check_consistency(prop_dir, _pdata)
            _params_check_text = format_params_block(_pdata)
            if _pchk["conflicts"]:
                _cl = "\n".join(
                    f"- {c['key']}：旧值 `{c['stale_pattern']}` 残留于 "
                    + ", ".join(f"{h['section']}×{h['count']}" for h in c['hits'])
                    for c in _pchk["conflicts"]
                )
                _params_check_text += (
                    f"\n⚠️ 程序化口径校验发现 {len(_pchk['conflicts'])} 个旧值残留"
                    f"（以下位置与口径表互斥，每条按 indicator_red_lines."
                    f"consistency_check 计 critical）：\n{_cl}\n"
                )
    except Exception:
        _params_check_text = ""

    result = self._run_critic(
        proposal_id, prop_dir, project_type, round_num,
        critic_writer_timeout_s(section_key),  # v6.8.52: 大模块 1200s，其余 900s
        focus_section=focus_section, is_full_review=is_full_review,
        ai_check_result=ai_check,  # v6.8.7: 传入程序化检测结果
        params_check_text=_params_check_text,  # v7.2.13
    )
    report_path = prop_dir / "05_review" / f"critic-round-{round_num}-{section_key}.md"
    if not result.get("success"):
        if self._salvage_critic_report(report_path, job):
            if _log:
                _log.warning(
                    f"[{proposal_id}] {section_key} 评审失败（{result.get('error')}），"
                    f"但报告已在本次开工后完整落盘，按成功结算（避免重跑）"
                )
            result = {"success": True, "salvaged": True}
        else:
            return {"success": False, "error": result.get("error", "critic 失败")}

    # 等待报告落盘（v6.10.26: section 感知路径——_run_critic 已按 section 分文件写盘）
    if not (report_path.exists() and report_path.stat().st_size > 100):
        self._wait_for_critic_report(report_path, timeout=30)

    # 解析报告，决定是否需要 researcher
    # v6.8.3-fix10: references 模块不插入 researcher 链（本身就是文献检验）
    # v7.3.0: method_manual 模块同样不插入（手册素材来自 KB 方法页素材包，
    # 走 update 阶段的 source_hint 机制，不是文献检索缺口）
    report = self._read_critic_report(prop_dir, round_num, section_key)
    if section_key not in ("references", "method_manual"):
        if report["dim_scores"].get("rigor", 1.0) < 0.70 or self._has_lit_gap({"output": report["output"]}):
            self._insert_researcher_pipeline(proposal_id, round_num, section["key"])
    # v7.3.10: 执行预演断链核销跟踪——rehearsal 报告存在时，把断链清单写回
    # 报告头部（供 writer 缺口驱动升级消费：_read_critic_report 读盘即得）
    if section_key == "method_manual":
        try:
            _reh = sorted((prop_dir / "05_review").glob("execution-rehearsal*.md"))
            if _reh and report_path.exists():
                _rt = _reh[-1].read_text(encoding="utf-8")
                _marker = "<!-- rehearsal-gaps-injected -->"
                if _marker not in report_path.read_text(encoding="utf-8"):
                    _inject = (
                        f"\n{_marker}\n\n## 附录：执行预演断链清单（{_reh[-1].name}，v7.3.10 注入）\n\n"
                        f"以下为第三方执行者按手册开工的推演断链——writer 逐条核销，"
                        f"critic 下轮逐条复核「预演断链#N 已修」标注：\n\n{_rt[:2600]}\n"
                    )
                    with open(report_path, "a", encoding="utf-8") as _fh:
                        _fh.write(_inject)
                    if _log:
                        _log.info(f"[{proposal_id}] 预演断链已注入手册评审报告（{_reh[-1].name}）")
        except Exception as _e:
            if _log:
                _log.debug(f"[{proposal_id}] 预演断链注入失败（fail-open）: {_e}")

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
    report = self._read_critic_report(prop_dir, round_num, section_key)
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

    # ── v6.10.55 单发化：直调快路径 ──
    # 任务形态是"读内嵌评审报告 → 吐一段 JSON"，单发结构化调用即可，
    # 无需 agent loop（系统提示 + 工具轮的 token 放大，M3 reasoning
    # token 随 turn 数膨胀）。直调输出必须能解析出 gaps JSON 才算成功，
    # 否则降级 agent loop（保留原方案A作为兜底，链路行为不变）。
    raw_text = ""
    method_tag = ""
    direct_attempted = False
    if llm_router is not None:
        direct_attempted = True
        try:
            call_result = llm_router.call_llm(
                "你是一位严谨的学术研究助手，只输出合法 JSON。",
                [{"role": "user", "content": fallback_prompt}],
                timeout=120,
                prefer="governance",  # v7.3.86: gaps JSON 为结构化判断任务，glm-first
            )
            raw = call_result[0] if isinstance(call_result, tuple) else call_result
            cand = (raw or "").strip()
            if cand and _extract_gaps_json(cand) is not None:
                raw_text = cand
                method_tag = "direct"
            elif _log:
                _log.info(f"[{proposal_id}] gap_identify 直调输出非 JSON gaps，转 agent loop")
        except Exception as e:
            if _log:
                _log.warning(f"[{proposal_id}] gap_identify 直调失败: {str(e)[:120]}")

    agent_success = False
    if not raw_text:
        # 步骤2（兜底）：hermes researcher agent loop
        # v7.2.2: 引用模块级符号（v7.2.2 修复点）
        # v7.3.45: 超时梯度化（基线 300 覆盖 p90=284s，重试 +120 护尾部）
        agent_result = _run_hermes_agent(
            "researcher", agent_prompt, timeout=_step_hermes_timeout(job, 360)
        )
        agent_success = agent_result.get("success", False)
        if direct_attempted:
            # v6.8.3: 记录降级事件到 proposal_state（口径对齐原
            # agent_loop_failed→llm_direct，方向反转为 direct_failed→agent_loop）
            self._mark_degradation(proposal_id, "gap_identify", "direct_failed→agent_loop")
        if agent_success:
            raw_text = agent_result.get("output", "")
            method_tag = "agent_loop_fallback"
            if _log:
                _log.info(
                    f"[{proposal_id}] gap_identify agent loop 成功 "
                    f"elapsed={agent_result.get('elapsed_s', 0)}s"
                )
        else:
            err = str(agent_result.get("error", "agent loop 失败"))[:300]
            _write_memory("researcher",
                f"[{now_utc()}] gap_identify 失败（课题：{proposal_id}，轮次：{round_num}，"
                f"章节：{section_name}）— 直调与 agent loop 均失败: {err}"
            )
            if _log:
                _log.warning(f"[{proposal_id}] gap_identify 直调与 agent loop 均失败: {err}")
            return {"success": False, "error": err}

    # 解析输出（raw_text 已通过 _extract_gaps_json 校验时必然成功）
    try:
        text = raw_text.strip()
        if not text:
            if _log:
                _log.warning(f"[{proposal_id}] gap_identify agent 输出为空，跳过")
            # 空 output 时写一个默认空 gap 文件，让后续步骤可以继续
            default_data = {"gaps": [], "note": "agent loop 输出为空，使用 critic 报告原始关键词"}
            gap_path.write_text(json.dumps(default_data, ensure_ascii=False, indent=2), encoding="utf-8")
            return {"success": True, "gap_path": str(gap_path), "method": "empty_fallback", "gap_count": 0}

        data = _extract_gaps_json(text)

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

        data.setdefault("section", section_key)
        gap_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        # 步骤3：回写 researcher profile 记忆
        gap_count = len(data["gaps"])
        high_pri = sum(1 for g in data["gaps"] if g.get("priority") == "high")
        keywords = []
        for g in data["gaps"]:
            keywords.extend(g.get("search_keywords", []))
        keyword_summary = "、".join(list(dict.fromkeys(keywords))[:5])

        method_tag = method_tag or "empty_fallback"
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
    # v6.10.6: 优先本章节的 gap 文件（防跨章节串读）；旧文件无 section
    # 字段时回退最新（保持向后兼容）。
    for _gf in gap_files:
        try:
            if json.loads(_gf.read_text(encoding="utf-8")).get("section") == section_key:
                gap_path = _gf
                break
        except Exception:
            continue

    import json
    gap_data = json.loads(gap_path.read_text(encoding="utf-8"))
    gaps = gap_data.get("gaps", [])
    all_keywords = []
    for g in gaps:
        all_keywords.extend(g.get("search_keywords", []))
    gap_keywords = list(dict.fromkeys(all_keywords))[:10]
    keyword_str = "、".join(gap_keywords)

    # v6.10.41: 空缺口短路——gap_identify 产出 0 缺口/0 关键词时（09-23
    # 实测 quantum-geometry R8 scheme 轮 gap-analysis gaps=0），旧链路照样
    # 派发：agent loop 白跑一趟回答"关键词为空"（浪费 1 会话），多源回退
    # 又用默认词 "high harmonic generation" 捞回 2010/2011 年泛域老文，
    # lit_read 再烧 5 个会话深读低价值文献——单次空缺口约 6 会话纯浪费。
    # 短路动作：写一份带章节标记的空 lit-gap 文件（lit_read 按 v6.10.6
    # 章节匹配读到它 → 无 arxiv_id → 跳过），不消耗任何 LLM 会话。
    if not gap_keywords:
        # v7.2.2: 引用模块级符号（v7.2.2 修复点）
        target_dir = prop_dir / "02_literature" / "targeted-research"
        target_dir.mkdir(parents=True, exist_ok=True)
        import time as _t
        result_path = target_dir / f"lit-gap-{int(_t.time())}.md"
        result_path.write_text(
            f"# 定向文献检索报告\n\n## 课题\n{proposal_id}\n\n"
            f"## 章节\n{section_key}\n\n"
            f"## 检索关键词\n- （本轮无文献缺口，未检索）\n\n"
            f"## 检索结果\n（critic 未识别文献缺口，本轮跳过定向检索）\n",
            encoding="utf-8",
        )
        _write_memory("researcher",
            f"[{now_utc()}] lit_search 短路（gap=0）— 课题：{proposal_id}，"
            f"轮次：{round_num}，章节：{section_name}：critic 未识别缺口，"
            f"未消耗检索会话"
        )
        if _log:
            _log.info(f"[{proposal_id}] lit_search 短路: gap=0 无关键词，跳过检索会话")
        return {
            "success": True, "result_path": str(result_path),
            "method": "short_circuit", "paper_count": 0,
        }

    # 步骤1：尝试 hermes researcher agent loop 联网检索
    # v7.2.2: 引用模块级符号（v7.2.2 修复点）
    agent_success = False
    papers = []

    # 复用 LiteratureService 的去重机制：获取已有论文 ID 集合
    from literature_service import LiteratureService
    _svc = LiteratureService()
    _local_ids = set(_svc._scan_local_raw_papers().keys())
    _exclude_ids = _svc._get_exclude_ids(proposal_id)
    _all_known = _local_ids | _exclude_ids
    _exclude_count = len(_all_known)

    # v6.10.41: 排除清单截断——旧实现把全部本地论文 ID（09-23 实测 1408 个
    # ≈16.5K 字符/4-8K token）注入每次 lit_search prompt，随 KB 增长线性
    # 膨胀；而解析后本就有程序化去重（is_new 标记 + 多源 existing_keys），
    # LLM 侧全量过滤与之职责重叠，属纯 token 开销。改为：仅提示总量 +
    # 采样 80 个 ID 示例，完整去重由系统程序化执行。
    _EXCLUDE_SAMPLE_CAP = 80
    _exclude_prompt = ""
    if _all_known:
        _sample = sorted(str(x) for x in _all_known)[:_EXCLUDE_SAMPLE_CAP]
        _exclude_prompt = (
            f"\n\n【请优先检索未处理过的新论文（本地已收录 {_exclude_count} 篇，"
            f"以下为其中部分 ID 示例；完整去重由系统在结果入库时程序化执行，"
            f"无需逐条比对）】\n"
            + "\n".join(_sample)
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
        # v7.3.45: 超时梯度化（基线 420 贴 p99=372s，重试 +120）
        agent_result = _run_hermes_agent(
            "researcher", agent_prompt, timeout=_step_hermes_timeout(job, 420)
        )
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

    # v6.10.35: 多源学术检索补充（真实 job 路径移植）——v6.10.32 曾把三源
    # 并发/year_from/BibTeX 加在 optimize._run_literature_searcher，但该函数
    # 只被旧版单 job 兼容路径（_run_researcher_step）调用，job 链的 lit_search
    # 实际走本函数（hermes agent loop 优先），更新落在了死路径上（09-21
    # 实测报告无多源章节/无 .bib 副产物/无补充日志）。此处对齐：
    #   ① search_academic 三源并发叠加（arxiv+openalex+semantic_scholar，
    #      失败静默降级不阻塞）；
    #   ② references/full_review 轮 year_from=当前年-3（references 轮本身
    #      无 lit_search job，full_review 检索是 references 时效补充的实际
    #      载体；经典文献由不限年的 agent loop 检索提供，多源层专注补新）；
    #   ③ 候选文献落 candidates-{ts}.bib，writer 修订 references.md 直接
    #      取标准条目。
    multi_source_papers = []
    bib_path = None
    search_sources = ("arxiv", "openalex")
    year_from = None
    try:
        import external_fetcher as ef
        from proposal_lifecycle.optimize import _multi_source_search_config
        combined_query = " ".join(gap_keywords[:2]) if gap_keywords else "high harmonic generation"
        # focus_section 在 full_review 轮为 None，按 section_key 构造以触发
        # 时效过滤分支（references/full_review 限近 3 年）
        search_sources, year_from = _multi_source_search_config(
            {"key": section_key} if section_key else None)
        oa_papers = ef.search_academic(
            combined_query, max_results=5,
            sources=search_sources, year_from=year_from,
        )
        existing_keys = set()
        for p in papers:
            aid = p.get("arxiv_id", "")
            if aid:
                existing_keys.add(f"arxiv:{aid}")
        for p in oa_papers:
            aid = p.get("arxiv_id", "")
            doi = (p.get("doi") or "").replace("https://doi.org/", "")
            title_key = str(p.get("title", "")).strip().lower()[:80]
            key = f"arxiv:{aid}" if aid else (f"doi:{doi}" if doi else f"title:{title_key}")
            if key not in existing_keys:
                existing_keys.add(key)
                multi_source_papers.append(p)
        if multi_source_papers:
            bib_path = target_dir / f"candidates-{int(_t.time())}.bib"
            try:
                bib_path.write_text(
                    ef.format_bibtex(multi_source_papers), encoding="utf-8")
            except Exception:
                bib_path = None
        if _log and multi_source_papers:
            _log.info(
                f"[{proposal_id}] 多源检索补充 {len(multi_source_papers)} 篇"
                f"（{'+'.join(search_sources)}，去重后"
                f"{f'，限 {year_from} 年后' if year_from else ''}）"
            )
    except Exception as e:
        if _log:
            _log.warning(f"[{proposal_id}] 多源学术检索失败（降级跳过）: {e}")

    lines = [f"# 定向文献检索报告\n", f"## 课题\n{proposal_id}\n"]
    lines.append(f"## 章节\n{section_key}\n")
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

    # v6.10.35: 多源补充章节（三源并发聚合结果 + BibTeX 副产物路径）
    if multi_source_papers:
        lines.append(f"\n## 多源学术检索补充（{'+'.join(search_sources)}）\n")
        if bib_path:
            lines.append(f"标准引用格式（可直接用于 references.md 修订）：{bib_path}\n")
        for p in multi_source_papers:
            aid = p.get("arxiv_id", "")
            doi = (p.get("doi") or "").replace("https://doi.org/", "")
            authors_list = p.get("authors", [])
            authors_str = ", ".join(authors_list[:3]) if isinstance(authors_list, list) else str(authors_list)
            ident = f"arXiv:{aid}" if aid else (f"DOI:{doi}" if doi else "无ID")
            abstract = (p.get("abstract") or "")[:150]
            lines.append(
                f"- {ident} | {p.get('title', '')} | {authors_str} | {p.get('year', '')} | "
                f"{p.get('venue', '')} | 引用:{p.get('citation_count', 0)} | "
                f"来源：{p.get('source', 'academic')} | {abstract}"
            )

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

    # 找到本轮最新的 lit-gap 报告（v6.10.6: 优先本章节，防跨章节串读）
    section_key = job.get("section_key", "rationale")
    targeted_dir = prop_dir / "02_literature" / "targeted-research"
    lit_files = sorted(targeted_dir.glob("lit-gap-*.md"), reverse=True)
    if not lit_files:
        return {"success": False, "error": "未找到文献检索报告"}
    lit_path = lit_files[0]
    for _lf in lit_files:
        try:
            _head = _lf.read_text(encoding="utf-8")[:400]
            if f"## 章节\n{section_key}\n" in _head:
                lit_path = _lf
                break
        except Exception:
            continue

    import re
    text = lit_path.read_text(encoding="utf-8")
    # v6.10.55 分诊：解析报告条目（id|标题|tldr），按检索关键词命中排序，
    # 深读上限 5→3（纯程序化，零 LLM）。M3 深读是链内最贵的执行操作，
    # 盲读 5 篇的尾部通常与缺口弱相关；报告格式漂移时回退原序全量正则
    # （保持旧上限 5，不因解析失败降低覆盖）。
    papers = _parse_lit_report_papers(text)
    if papers:
        _kw_line = ""
        _km = re.search(r"## 检索关键词\n-\s*(.+)", text)
        if _km:
            _kw_line = _km.group(1)
        arxiv_ids = _rank_lit_read_ids(papers, _kw_line, cap=_LIT_READ_CAP)
        if _log:
            _log.info(
                f"[{proposal_id}] lit_read 分诊: 报告 {len(papers)} 篇 → "
                f"深读 {len(arxiv_ids)} 篇（cap={_LIT_READ_CAP}）"
            )
    else:
        arxiv_ids = re.findall(r"(\d{4}\.\d{4,5})", text)

    if not arxiv_ids:
        if _log:
            _log.info(f"[{proposal_id}] lit_read 跳过: 无 arxiv_id 可读（lit_search 未返回论文）")
        return {"success": True, "notes_path": "", "read_count": 0, "reason": "无论文可读"}

    notes = []
    read_count = 0
    agent_success = False

    # 步骤1：hermes researcher agent loop 深度阅读
    # v6.10.41: 5 篇合并单会话——旧实现逐篇各开一次 oneshot 会话（5 篇 =
    # 5 个完整 agent 会话：系统提示 + 多轮 web_search，约占轮内 LLM 会话
    # 量的 45%）。合并后一次带 5 篇，按 "## <arXiv ID>" 分节输出；输出
    # 截断/缺失的篇目降级 LiteratureService.read 单篇兜底（与旧降级路径
    # 同源）。timeout 240→600（单会话串行读 5 篇）。
    # v7.2.2: 引用模块级符号（v7.2.2 修复点）

    _aids = arxiv_ids[:5]
    _MIN_NOTE_CHARS = 120  # 单篇有效笔记门槛（低于视为截断/缺失）

    def _fallback_read(aid: str) -> bool:
        """单篇降级直读（LiteratureService），成功计入 notes 并返回 True。"""
        try:
            from literature_service import LiteratureService
            svc = LiteratureService()
            result = svc.read(aid, proposal_id=proposal_id)
            if result.get("content"):
                notes.append(f"## {aid}\n\n{result['content']}\n")
                return True
        except Exception as e:
            if _log:
                _log.warning(f"[{proposal_id}] lit_read 降级直读失败 {aid}: {e}")
        return False

    # v7.0.0: 五维笔记方法论（研究问题/背景/方法/主要发现/潜在方向五段
    # 定义）已收敛至 .hermes/skills/literature-reading/SKILL.md 一节，
    # 经 skill_loader 按节裁剪注入；prompt 只保留编排契约（"## <arXiv
    # ID>" 分节、顺序、6500 字上限、清单格式）。fail-open：skill 缺失
    # 返回空串，不阻塞深读与 _MIN_NOTE_CHARS 降级链路。
    try:
        from skill_loader import inject_block
        _lit_skill = inject_block(
            "literature-reading", ["一、五维笔记"], note="深读标准"
        )
    except Exception:
        _lit_skill = ""

    agent_prompt = (
        f"你是一位专业研究助手（Researcher）。请逐一深度阅读以下 "
        f"{len(_aids)} 篇论文（课题：{proposal_id}），并为每篇整理结构化笔记。\n\n"
        f"【arXiv ID 清单】\n" + "\n".join(f"- {aid}" for aid in _aids) + "\n\n"
        f"请执行：\n"
        f"1. 使用 web_search 逐一获取每篇论文的完整信息（标题、作者、摘要等）\n"
        f"2. 对每篇论文输出一个独立笔记段落，必须以 '## <arXiv ID>' 行开头"
        f"（如 '## {_aids[0]}'），共 {len(_aids)} 段，顺序与清单一致\n"
        f"3. 每段按下方 skill 深读标准，以 '### <维度>' 子标题整理五个维度、"
        f"每个维度 2-3 句实质内容。\n\n"
        f"{_lit_skill}\n"
        f"注意：总输出控制在 6500 字以内；只输出清单内论文的笔记，不要输出其他内容。\n"
    )

    try:
        # v7.3.45: 超时梯度化（基线 660 覆盖 max 成功 531s，重试 +120）
        agent_result = _run_hermes_agent(
            "researcher", agent_prompt, timeout=_step_hermes_timeout(job, 660)
        )
        if agent_result.get("success"):
            output = agent_result.get("output", "")
            # 解析 "## <aid>" 分节
            parts = re.split(r"\n?##\s+(\d{4}\.\d{4,5})", output)
            per_aid: Dict[str, str] = {}
            for i in range(1, len(parts) - 1, 2):
                per_aid[parts[i]] = parts[i + 1].strip()
            for aid in _aids:
                body = per_aid.get(aid, "")
                if len(body) >= _MIN_NOTE_CHARS:
                    agent_success = True
                    notes.append(f"## {aid}\n\n{body}\n")
                    read_count += 1
                    # v6.8.18 fix: 建立 wiki/papers/{aid}.md 页面（lit_note
                    # .link_to_proposal() 依赖），仅页面不存在时写入。
                    try:
                        from literature_service import LiteratureService
                        svc = LiteratureService()
                        existing = svc._get_wiki_paper_note(aid)
                        if not existing:
                            svc._save_wiki_paper_note(aid, body, proposal_id)
                            svc._update_read_status(aid, "deep-read", proposal_id)
                    except Exception as wiki_e:
                        if _log:
                            _log.warning(
                                f"[{proposal_id}] lit_read 成功但 wiki 写入失败 {aid}: {wiki_e}"
                            )
                else:
                    if _log:
                        _log.info(
                            f"[{proposal_id}] lit_read 合并会话缺 {aid} 笔记"
                            f"（{len(body)} 字符），降级单篇直读"
                        )
                    if _fallback_read(aid):
                        read_count += 1
            if _log:
                _log.info(
                    f"[{proposal_id}] lit_read 合并会话完成: "
                    f"{len(per_aid)}/{len(_aids)} 篇有笔记"
                )
        else:
            if _log:
                _log.warning(
                    f"[{proposal_id}] lit_read 合并 agent loop 失败，批量降级直读: "
                    f"{agent_result.get('error', '')}"
                )
            for aid in _aids:
                if _fallback_read(aid):
                    read_count += 1
    except Exception as e:
        if _log:
            _log.warning(f"[{proposal_id}] lit_read 合并 agent loop 异常: {e}")
        for aid in _aids:
            if _fallback_read(aid):
                read_count += 1

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

            # v6.10.6: 优先本章节报告（防跨章节串读），无标记时回退最新
            section_key = job.get("section_key", "rationale")
            lit_path = lit_files[0]
            for _lf in lit_files:
                try:
                    if f"## 章节\n{section_key}\n" in _lf.read_text(encoding="utf-8")[:400]:
                        lit_path = _lf
                        break
                except Exception:
                    continue
            text = lit_path.read_text(encoding="utf-8")
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
    report = self._read_critic_report(prop_dir, round_num, section_key)
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
    report = self._read_critic_report(prop_dir, round_num, section_key)
    dim_scores = report["dim_scores"]
    weakest_dim = self._get_weakest_dimension(dim_scores)

    # v6.9.62: 维度完整性校验——按评分口径取期望维度集。
    # v7.2.41 BUG-8 修复：旧版用 DIMENSION_FLOOR 全集（含 completeness）
    # 对正文章节轮判完备性，而 completeness 是 references 专轮专属维度，
    # 正文轮永不产出 → dims_partial 恒 True（实测 148/148），
    # 把 completion.py 六道质量门与看板 4 维全部封死。改为口径感知。
    dims_partial, dims_present, _dims_missing = judge_dims_partial(
        section_key, dim_scores
    )
    if dims_partial and _log:
        _log.warning(
            f"[{proposal_id}] r{round_num} {section_key} 维度解析不完整: "
            f"{dims_present}（缺 {_dims_missing}），"
            f"本轮分数为残缺口径"
        )

    # v6.7.6: writer 修改前备份当前申请书，供 monitor 比对
    proposal_path = prop_dir / "04_proposal" / "proposal-draft.md"
    backup_path = prop_dir / "04_proposal" / f"proposal-draft-r{round_num - 1}.md"
    if proposal_path.exists() and proposal_path.stat().st_size > 100:
        try:
            shutil.copy2(str(proposal_path), str(backup_path))
        except Exception:
            pass

    # 构造 lit_supplement：使用本 proposal 下 targeted-research 目录最新文件
    # v6.10.41: 章节感知 + 空报告过滤——旧实现盲取最新 lit 文件：可能指向
    # 其他章节的检索报告（跨章节串读），或指向 v6.10.41 短路落盘的空报告
    # （gap=0 无新文献），两种情况都误导 writer 去找不存在的文献。
    lit_supplement = ""
    targeted_dir = prop_dir / "02_literature" / "targeted-research"
    if targeted_dir.exists():
        lit_files = sorted(targeted_dir.glob("lit-gap-*.md"), reverse=True)
        _lit_file = lit_files[0] if lit_files else None
        for _lf in lit_files:
            try:
                if f"## 章节\n{section_key}\n" in _lf.read_text(encoding="utf-8")[:400]:
                    _lit_file = _lf
                    break
            except Exception:
                continue
        if _lit_file is not None:
            try:
                _lit_head = _lit_file.read_text(encoding="utf-8")[:400]
            except Exception:
                _lit_head = ""
            if "无文献缺口" not in _lit_head and "跳过定向检索" not in _lit_head:
                lit_supplement = (
                    f"\n【文献补充（researcher 定向检索）】\n"
                    f"请参考 {_lit_file} 中的新文献，在修订时引用。\n"
                )

    # v6.9.30: 程序化 AI 写作模式检测——writer 步骤重新运行（与 critic 步骤
    # 结果一致，确定性），注入 writer prompt 并用于后续评分 cap
    from proposal_sections import ProposalSections
    sections_obj = ProposalSections(prop_dir / "04_proposal")
    sections_obj.ensure_split()
    ai_check = self._detect_ai_patterns(prop_dir, sections_obj)
    # v6.9.54: 预算门基线——writer 写入前记录聚焦章节字数，
    # 写入后据此判定"预算内 或 本轮净删 ≥10%"（超限章节渐进收敛）。
    _sections_dir = prop_dir / "04_proposal" / "sections"
    before_chars = (
        section_char_count(_sections_dir, section_key)
        if section_char_count else None
    )
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

    # v7.2.13: 数值口径表注入——params.json 存在时，writer 必须按单一
    # 真相源口径写作（根治跨章数值互斥：moire R4-R8 每轮 4/4 章节复现）。
    # fail-open：无表 → 空串注入。
    _params_supplement = ""
    try:
        from .params_registry import load_params, format_params_block
        _params_data = load_params(prop_dir)
        if _params_data:
            _params_supplement = format_params_block(_params_data)
    except Exception:
        _params_supplement = ""

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
        round_num=round_num,  # v6.10.26: 报告读盘按 section 分流
        params_supplement=_params_supplement,  # v7.2.13
    )
    if not writer_result.get("success"):
        return {"success": False, "error": writer_result.get("error", "writer 失败")}

    # v7.2.67: draft 同步守卫——sections 任一文件比 proposal-draft.md 新则
    # 立即重组（修 A 类缺陷：mos2 曾 draft 3GV/m vs sections 6.1GV/m 失同步、
    # attosecond 检索截止日期两版；下游若读 draft 而非 sections，已修复的
    # 错误会复活）。零 LLM。
    try:
        from proposal_sections import ProposalSections as _PS
        _draft = prop_dir / "04_proposal" / "proposal-draft.md"
        _sec_dir = prop_dir / "04_proposal" / "sections"
        if _sec_dir.exists():
            _newest_sec = max(f.stat().st_mtime for f in _sec_dir.glob("*.md"))
            if (not _draft.exists()) or (_draft.stat().st_mtime < _newest_sec):
                _PS(prop_dir / "04_proposal").assemble_draft()
                if _log:
                    _log.info(f"[{proposal_id}] draft 落后于 sections，已自动重组")
    except Exception as _e:
        if _log:
            _log.debug(f"[{proposal_id}] draft 同步守卫异常（fail-open）: {_e}")

    # v7.2.32: 写后质量门——KB 引用守卫（v7.2.30 wikilink 节点格式）
    # + 6 章节硬模板守卫（v7.2.30 structure_guard）。
    # 任何 fail 不阻断当前 job（fail-open 原则），仅入 prop_state.quality_warning
    # 让下轮 critic 能看到。两个守卫零 LLM（grep + 关键词分类），< 100ms。
    try:
        from kb_pack_wikilink_guard import check_proposal as _wl_check
        from proposal_structure_guard import check_proposal as _str_check
        _wl = _wl_check(proposal_id)
        _st = _str_check(proposal_id)
        # 入 quality_warning（不阻断 job）
        _warnings = []
        if _wl.get("status") == "fail":
            _warnings.append(
                f"KB引用 0/{_wl.get('total_refs', 0)}（wikilink 守卫 v7.2.30 fail）："
                f"下轮 writer 必须从 kb-methods-pack.md 引用至少 3 个 [[methods/<slug>]]")
        elif _wl.get("status") == "warn":
            _warnings.append(
                f"KB引用 {_wl.get('total_refs', 0)}/3（不达标）：建议补到 ≥3")
        if _st.get("status") == "fail":
            _missing = "、".join(_st.get("missing", []))
            _warnings.append(
                f"6章节缺 {_missing}（structure_guard v7.2.30 fail）："
                f"下轮 writer 必须按 SKILL.md §七 补齐 6 个 H2 章节")
        if _warnings:
            try:
                _ps = self._get_proposal_state(proposal_id) or {}
                _existing = _ps.get("quality_warning") or ""
                # v7.2.61: 守卫警告改为「当前状态覆盖式」——守卫每次 writer job
                # 都会重跑，其结果代表当前状态而非历史。旧版无限追加导致
                # ssh-weyl 的 quality_warning 堆积 24 行重复噪音（决策包全量
                # 粘贴后用户看到同两行警告 ×12）。现只保留非守卫类历史警告
                # （如逃生阀晋级警告）+ 本轮最新守卫结果，且整行去重。
                _guard_prefixes = ("KB引用", "6章节缺")
                _kept = [
                    ln for ln in _existing.splitlines()
                    if ln.strip() and not ln.strip().startswith(_guard_prefixes)
                ]
                _seen: set = set()
                _merged: list = []
                for ln in _kept + _warnings:
                    if ln not in _seen:
                        _seen.add(ln)
                        _merged.append(ln)
                _ps["quality_warning"] = "\n".join(_merged)
                self._set_proposal_state(proposal_id, _ps)
            except Exception:
                pass
            if _log:
                _log.warning(
                    f"[{proposal_id}] r{round_num} 写后质量门："
                    + " | ".join(_warnings))
    except Exception as e:
        if _log:
            _log.debug(f"[{proposal_id}] 写后质量门异常（fail-open）: {e}")

    # v7.2.13: 落盘后零 LLM 口径校验——stale 旧值残留 grep 全章节，
    # 冲突写 05_review/params-conflicts.json（下轮 critic 与 monitor 消费）
    if _params_supplement:
        try:
            from .params_registry import run_check_and_persist
            _pc = run_check_and_persist(prop_dir, round_num=round_num)
            if _pc.get("active") and _pc.get("conflicts"):
                if _log:
                    _log.warning(
                        f"[{proposal_id}] r{round_num} 口径校验："
                        f"{len(_pc['conflicts'])} 个旧值残留 "
                        f"（详见 05_review/params-conflicts.json）"
                    )
        except Exception as e:
            if _log:
                _log.warning(f"[{proposal_id}] 口径校验异常（fail-open）: {e}")

    # v7.2.19: AI 模式写后自检门（回弹治理，用户裁决「执行」对策 3）——
    # 写前注入清单仍回弹的实证：mos2 超长句 R2 13 处→R3 25 处、修复句
    # 本身引入新禁用词（"口径"2 处系本轮修复句新增），expression 被程序
    # 天花板封在 0.62。光靠写前清单不够，落盘后须验证闭环：超长句较写前
    # 回弹 或 ceiling<0.7 → 触发一次「仅修句」补丁会话；补丁后复检并
    # 记录，仍超标 warning 放行（fail-open 不阻塞 job，宁可下轮继续）。
    if section_key in ("rationale", "content", "scheme"):
        try:
            _post_check = self._detect_ai_patterns(
                prop_dir, sections_obj, section_key=section_key)
            _pre_ls = ((section_baseline or {}).get("details", {})
                       .get("long_sentences", {}) or {})
            _post_ls = (_post_check.get("details", {})
                        .get("long_sentences", {}) or {})
            _pre_n = _pre_ls.get("count", 0)
            _post_n = _post_ls.get("count", 0)
            _rebound = section_baseline is not None and _post_n > _pre_n
            _severe = _post_check.get("ceiling", 1.0) < 0.7
            if (_rebound or _severe) and _post_n > 0:
                if _log:
                    _log.warning(
                        f"[{proposal_id}] r{round_num} {section_key} 写后自检门触发："
                        f"超长句 {_pre_n}→{_post_n}"
                        f"{'（回弹）' if _rebound else ''}"
                        + (f"（ceiling {_post_check.get('ceiling', 0):.2f}）" if _severe else "")
                        + "，发起仅修句补丁"
                    )
                _fix_prompt = (
                    f"你刚修改的 {prop_dir}/04_proposal/sections/{section_key}.md "
                    f"存在 {_post_n} 处超过 120 字的超长句（写前 {_pre_n} 处，出现回弹）。\n"
                    f"仅做拆句与衔接修复：把超长句按语义拆为 ≤100 字短句，"
                    f"用内容驱动衔接（禁用「进而/据此/综上」等死板关联词）。\n"
                    f"红线：禁止改动任何技术内容、数值、公式、引用编号与章节结构；"
                    f"禁止引入新术语。\n"
                    f"修复后直接写回同一文件，只输出一行完成说明。"
                )
                _patch = self._run_hermes("writer", _fix_prompt, timeout=600)
                if _patch.get("success"):
                    _recheck = self._detect_ai_patterns(
                        prop_dir, sections_obj, section_key=section_key)
                    _re_n = (_recheck.get("details", {})
                             .get("long_sentences", {}) or {}).get("count", _post_n)
                    if _log:
                        _log.info(
                            f"[{proposal_id}] r{round_num} {section_key} "
                            f"修句补丁完成：超长句 {_post_n}→{_re_n}"
                        )
        except Exception as e:
            if _log:
                _log.warning(f"[{proposal_id}] 写后自检门异常（fail-open）: {e}")

    # v6.9.54: 写入门卫——writer 落盘后、job 判定继续之前，确定性修复
    # 结构污染（references 工作日志剥离 / full_review 骨架重写）。
    # 根治点：污染在数据域的存活时间为零，不再依赖下一轮评审发现或
    # 人工一次性清理（v6.9.53 的 apply_all 从此只是历史存量工具）。
    if guard_written_artifacts:
        try:
            guard_result = guard_written_artifacts(prop_dir)
            for item in guard_result.get("repaired", []):
                if _log:
                    _log.info(f"[{proposal_id}] 写入门卫已修复: {item}")
            for err in guard_result.get("errors", []):
                if _log:
                    _log.warning(f"[{proposal_id}] 写入门卫异常（fail-open）: {err}")
        except Exception as e:
            if _log:
                _log.warning(f"[{proposal_id}] 写入门卫异常（fail-open）: {e}")

    # v6.9.55: 质量门（重构自预算门）——拦截冗余/无关这两类真质量缺陷：
    # 跨章节重复句（评审红线）、章节内成片重复论证、与课题核心术语
    # 脱钩的无关段落。字数超限不独立拦截——无缺陷命中的实质性长文放行
    # （字数是症状，冗余/无关才是病因）。未通过则 section_passed=False。
    quality_gate_result = None
    quality_ok = True
    if quality_gate:
        try:
            quality_gate_result = quality_gate(
                _sections_dir, section_key, before_chars, prop_dir=prop_dir)
            quality_ok = quality_gate_result.get("passed", True)
            if not quality_ok and _log:
                _log.warning(
                    f"[{proposal_id}] 质量门拦截: {quality_gate_result.get('reason')}"
                )
        except Exception as e:
            if _log:
                _log.warning(f"[{proposal_id}] 质量门异常（fail-open）: {e}")
            quality_gate_result = None
            quality_ok = True

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
    report = self._read_critic_report(prop_dir, round_num, section_key)
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

    # v6.8.8: references 评审专用计分——N/A 维度不纳入加权
    if section_key == "references" and dim_scores:
        ref_dims = {k: v for k, v in dim_scores.items() if k in ("rigor", "completeness") and v > 0}
        if ref_dims:
            score_after = sum(ref_dims.values()) / len(ref_dims)
            if _log:
                _log.info(f"[{proposal_id}] references 评审专用计分: {score_after:.2f} (dims={ref_dims})")

    # v6.8.8: 综合分天花板——scoring_integrity_rules.rule_1
    # v7.2.39（BUG-6）：必须排在 references 专用计分之后，否则 ref 重算会
    # 覆写 cap 结果（与 proposal_lifecycle/optimize.py 同源同修）。
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
    report_path = prop_dir / "05_review" / f"critic-round-{round_num}-{section_key}.md"
    if not report_path.exists():
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
        and quality_ok  # v6.9.55: 质量门——冗余/无关缺陷未修复不得通过（防膨胀毕业）
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
        # v6.9.55: 质量门判定入史——冗余/无关缺陷与收敛轨迹可观测
        "quality_gate_passed": quality_ok,
        "quality_gate_reason": (
            quality_gate_result.get("reason") if quality_gate_result else None
        ),
        "quality_over_budget": (
            quality_gate_result.get("over_budget") if quality_gate_result else None
        ),
        # v6.10.26: 口径标记入史（对齐 optimize.py v6.10.3）——references
        # 为 2 维专用口径（rigor/completeness），章节为 4 维加权口径。
        # 下游（周报/看板/dossier/逃生阀）据此分型绘制，防止异口径分
        # 被当整篇分读（实测 attosecond r5 rationale 被 references 裸文件
        # 污染成 2 维均值 0.66）。
        "caliber": "references_2d" if section_key == "references" else "section_4d",
        # v6.9.62: 维度完整性入史——残缺轮可观测，天花板/晋级检测过滤
        "dims_partial": dims_partial,
        "dims_present": dims_present,
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

    # v7.0.0: 四维评审方法论（清晰度/可检验性/切分合理性/一致性的维度
    # 定义）已收敛至 .hermes/skills/quality-review/SKILL.md 三节，经
    # skill_loader 按节裁剪注入；prompt 只保留编排契约（评分块输出格式
    # 与报告写入路径——_parse_idea_review_score 的解析口径不动）。
    # fail-open：skill 缺失返回空串，不阻塞评审循环。
    try:
        from skill_loader import inject_block
        _qr_skill = inject_block(
            "quality-review", ["三、研究设想评审"],
            note="四维评审标准，总分≥0.70通过",
        )
    except Exception:
        _qr_skill = ""

    # ── 评审循环 ──
    for attempt in range(1, MAX_IDEA_REVIEW_ATTEMPTS + 1):
        idea_content = idea_path.read_text(encoding="utf-8")

        # 1. 调用 researcher 评审研究设想
        review_prompt = (
            f"请对以下 NSFC 课题研究设想做独立质量评审。\n\n"
            f"【研究设想文件】\n{idea_path}\n"
            f"请读取该文件并做评审。\n\n"
            f"{_qr_skill}\n"
            f"请按上述四维评审标准逐维打分（每维 0-1 分）并指出具体问题，"
            f"在报告末尾包含评分块：\n"
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

    # ── v6.10.55 单发化：直调快路径 ──
    # brief 是小文件短输出（研究概要），单发调用 + 程序写盘 + 结构校验
    # 即可，无需 agent loop。校验不过（非 markdown/过短）回退原路径。
    # method_manual 不同：它是"读大文件改写"的 agent 形态任务，单发会
    # 把 40-60KB 全册压进一次 completion（M3 reasoning token 吃配额的
    # 长输出陷阱），故保留 agent loop 不动。
    direct_prompt = (
        f"请根据以下申请书内容，撰写课题设想/研究概要（将写入 {brief_path.name}）。\n\n"
        f"要求：\n"
        f"1. 用凝练的叙述风格概括研究问题、科学意义、核心创新、预期贡献\n"
        f"2. 不要罗列细节，突出研究思路主线\n"
        f"3. 输出为 markdown，包含 # 标题 和 > 项目类型等元信息\n"
        f"4. 只输出 markdown 正文，不要写入文件，不要任何额外说明\n\n"
        f"【申请书内容】\n{draft}\n"
    )
    if llm_router is not None:
        try:
            call_result = llm_router.call_llm(
                "你是一位 NSFC 申请书撰写助手，只输出 Markdown 正文。",
                [{"role": "user", "content": direct_prompt}],
                timeout=300,
            )
            text = (call_result[0] if isinstance(call_result, tuple) else call_result or "").strip()
            if _valid_brief_text(text):
                brief_path.write_text(text + "\n", encoding="utf-8")
                if _log:
                    _log.info(f"[{proposal_id}] update_vision 直调快路径成功（{len(text)} 字符）")
                return {"success": True, "brief_path": str(brief_path), "method": "direct"}
            if _log:
                _log.info(f"[{proposal_id}] update_vision 直调产物校验不过，回退 agent loop")
        except Exception as e:
            if _log:
                _log.warning(f"[{proposal_id}] update_vision 直调失败: {str(e)[:120]}")

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
    return {"success": True, "brief_path": str(brief_path), "method": "agent_loop"}


def _run_manual_critic_step(self, proposal_id: str, job: Dict[str, Any]) -> Dict[str, Any]:
    """v7.3.0: 方法手册就绪度评审（第六模块 method_manual 的 critic 步）。

    评审对象 03_method/method-manual.md（唯一真相源）；参照证据为方案章
    节选 + kb-methods-pack 素材包 + params.json 口径校验（零 LLM 预检）。
    2 维专用口径（readiness/rigor）+ L0-L4 就绪度分级（标准沉淀在
    .hermes/skills/method-manual/SKILL.md 四节），报告写
    05_review/critic-round-{n}-method_manual.md（与章节报告分文件，读盘
    走 _read_critic_report 通用路径）。
    """
    prop_dir = self._find_proposal_dir(proposal_id)
    if not prop_dir:
        return {"success": False, "error": "proposal 目录不存在"}

    prop_state = self._get_proposal_state(proposal_id)
    project_type = prop_state.get("project_type", "general")
    round_num = job["round"]

    method_dir = prop_dir / "03_method"
    manual_path = method_dir / "method-manual.md"
    pack_path = method_dir / "kb-methods-pack.md"
    scheme_path = prop_dir / "04_proposal" / "sections" / "scheme.md"
    report_path = prop_dir / "05_review" / f"critic-round-{round_num}-method_manual.md"

    # 零 LLM 预检：占位状态 / 体积 / 素材包 / 口径冲突
    manual_size = manual_path.stat().st_size if manual_path.exists() else 0
    _manual_head = ""
    if manual_path.exists():
        try:
            _manual_head = manual_path.read_text(encoding="utf-8")[:400]
        except Exception:
            _manual_head = ""
    is_placeholder = (
        manual_size < MANUAL_MIN_BYTES or "待课题进入优化环节后" in _manual_head
    )
    preflight_lines = [
        f"- 手册体积：{manual_size} 字节" + ("（占位/未实质开写）" if is_placeholder else ""),
        f"- KB 方法素材包（kb-methods-pack.md）：{'存在' if pack_path.exists() else '缺失（方法页引用无从落地，按要素⑧缺陷计）'}",
        f"- 研究方案章节：{'存在' if scheme_path.exists() else '缺失'}",
    ]

    # v7.2.13 同款：params.json 口径校验块（手册参数须与口径表一致）
    _params_check_text = ""
    try:
        from .params_registry import load_params, check_consistency, format_params_block
        _pdata = load_params(prop_dir)
        if _pdata:
            _pchk = check_consistency(prop_dir, _pdata)
            _params_check_text = format_params_block(_pdata)
            if _pchk["conflicts"]:
                _params_check_text += (
                    f"\n⚠️ 程序化口径校验发现 {len(_pchk['conflicts'])} 处旧值残留"
                    f"（手册与申请书口径表互斥，每处按要素⑧计 [high]）：\n"
                    + "\n".join(
                        f"- {c['key']}：旧值 `{c['stale_pattern']}` 残留"
                        for c in _pchk["conflicts"]
                    ) + "\n"
                )
    except Exception:
        _params_check_text = ""

    # 就绪度标准注入（skill 四节：八要素清单 + L0-L4 分级 + 评分契约）
    _mm_skill = ""
    try:
        from skill_loader import inject_block
        _mm_skill = inject_block(
            "method-manual", ["四、手册就绪度标准"], note="手册就绪度评审标准（八要素/L0-L4）"
        )
    except Exception:
        _mm_skill = ""

    prompt = (
        f"请对以下研究课题的方法学手册做第 {round_num} 轮**开工就绪度**评审。\n\n"
        f"【项目类型】{project_type}\n\n"
        f"【评审对象（手册全文）】{manual_path}\n"
        f"【参照证据】\n"
        f"- 研究方案章节（手册须覆盖其全部技术路线）：{scheme_path}\n"
        f"- KB 方法素材包（方法页参数溯源参照）：{pack_path}\n\n"
        f"【程序化预检（零 LLM，直接采信）】\n"
        + "\n".join(preflight_lines) + "\n"
        f"{_params_check_text}\n"
        f"{_mm_skill}\n"
        f"请执行（八要素清单化核查，先数档再打分）：\n"
        f"1. 读手册全文，按研究内容/技术路线逐项列出方法单元，核对要素①覆盖度——\n"
        f"   每项研究内容（R1/R2/R3…）都必须有对应方法单元，缺一项即 [critical]\n"
        f"2. 逐方法单元核对要素②-⑦：原理表述/参数表（数值+单位+出处，无来源须标\n"
        f"   '待标定'）/实施协议（步骤·装置·软件设置）/数据判据（Go-No-Go 与判据\n"
        f"   口径表一致）/失效模式与边界（No-Go·风险·替代方案）/资源估算（核时·机时）\n"
        f"3. 要素⑧溯源闭环：手册↔申请书口径表双向索引、KB 方法页引用是否落地\n"
        f"4. 对照 L0-L4 定义给出手册整体就绪度分级（先数过项数再定级，禁止印象式）\n\n"
        f"【报告输出契约（硬性）】\n"
        f"报告全文 ≤3000 字。问题清单每条一行：\n"
        f"`[severity]｜要素编号①-⑧｜位置（小节标题）｜问题≤40字｜建议≤40字`\n"
        f"报告末尾必须包含如下格式的评分块与就绪度行（纯文本行，数字不要加粗、\n"
        f"不要放表格，否则程序解析误读）：\n"
        f"```\n"
        f"## 评分\n"
        f"创新性：N/A\n"
        f"可行性：N/A\n"
        f"严谨性：0.75\n"
        f"就绪度：0.80\n"
        f"综合评分：0.78\n"
        f"手册就绪度：L2\n"
        f"```\n"
        f"（严谨性=参数溯源真实/数值可复算/口径一致；就绪度=八要素覆盖与可开工\n"
        f"程度；综合评分为两者均值。就绪度行格式必须是 `手册就绪度：L<数字>`。）\n"
        f"将评审报告写入：{report_path}\n"
    )
    result = self._run_hermes("critic", prompt, critic_writer_timeout_s("method_manual"))
    if not result.get("success"):
        if self._salvage_critic_report(report_path, job):
            if _log:
                _log.warning(
                    f"[{proposal_id}] 手册评审失败（{result.get('error')}），"
                    f"但报告已在本次开工后完整落盘，按成功结算（避免重跑）"
                )
        else:
            return {"success": False, "error": result.get("error", "手册评审失败")}

    # 等待报告落盘并校验可解析（与章节 critic 步同款容错）
    report_path.parent.mkdir(parents=True, exist_ok=True)
    if not (report_path.exists() and report_path.stat().st_size > 100):
        self._wait_for_critic_report(report_path, timeout=30)
    report = self._read_critic_report(prop_dir, round_num, "method_manual")
    if _log:
        _log.info(
            f"[{proposal_id}] 手册就绪度评审: score={report['score']}, "
            f"dims={report['dim_scores']}, issues={len(report['issues'])}"
        )
    return {"success": True, "score": report["score"]}


def _run_manual_writer_step(self, proposal_id: str, job: Dict[str, Any]) -> Dict[str, Any]:
    """v7.3.0: 方法手册两阶段升级（第六模块 method_manual 的 writer 步）。

    继承 update_method_manual 的两阶段机制（v7.2.11：规划→逐节执行，
    单会话小负载），并注入本轮手册 critic 的缺口清单——缺口驱动升级：
    critic 的每条 [critical]/[high] 缺口必须有对应 add/revise 动作
    （上限 6 动作，critical 优先）。

    完成后按 2 维口径（readiness/rigor）入史 score_history（caliber=
    manual_2d，不覆盖整篇 last_score——异口径不污染连续性判定），并写
    section_passes["method_manual"]：
      过线 = critic 分 ≥ min_overall_score（默认 0.85）
             且无 critical/high 缺口 且 两维无短板（<0.70）
             且就绪度 ≥ L3（MANUAL_READY_LEVEL，协议可执行=可开工）
             且手册实质内容 ≥ MANUAL_MIN_BYTES（超过注册占位）
    """
    prop_dir = self._find_proposal_dir(proposal_id)
    if not prop_dir:
        return {"success": False, "error": "proposal 目录不存在"}

    prop_state = self._get_proposal_state(proposal_id)
    project_type = prop_state.get("project_type", "general")
    round_num = job["round"]
    threshold = self._get_quality_threshold(project_type)

    # 读本轮手册 critic 报告（2 维口径 + 就绪度分级 + 缺口清单）
    report = self._read_critic_report(prop_dir, round_num, "method_manual")
    if not report.get("output"):
        return {"success": False, "error": "手册评审报告缺失（critic 前置步未产出）"}
    dim_scores = report.get("dim_scores") or {}
    issues = report.get("issues") or []
    score = float(report.get("score") or 0.0)

    readiness_level = -1
    _m = re.search(r"手册就绪度[：:]\s*L\s*([0-4])", report["output"])
    if _m:
        readiness_level = int(_m.group(1))

    gaps = [i for i in issues if i.get("severity") in ("critical", "high")]
    findings_block = ""
    if gaps:
        # v7.3.27: 缺口清单不再截断到 10 条/120 字——houston r2 实测 18 条
        # （11 critical + 7 high），第 11 条 critical（§0.8 Up 窗口）恰被
        # 截掉且从未进过计划；critic 的单行建议普遍 116–167 字，120 字会在
        # 建议中段截断，writer 只看到"问题"看不到"怎么改"。
        _lines = [f"- [{i['severity']}] {i.get('line', '')[:200]}" for i in gaps[:20]]
        findings_block = (
            f"■ 本轮手册评审缺口（缺口驱动升级——每条 [critical]/[high] 缺口"
            f"必须有对应 add/revise 动作，critical 最优先）：\n"
            + "\n".join(_lines) + "\n\n"
        )

    # 两阶段升级（critic 缺口驱动版；模块级直调防 mock 短路，与 legacy 步同款）
    update = _manual_two_phase_update(
        self,
        proposal_id, prop_dir,
        plan_extra=findings_block,
        max_actions=6,
        skill_sections=("一、更新纪律", "四、手册就绪度标准"),
        plan_note="手册维护强制纪律 + 就绪度八要素标准",
        plan_timeout=480,  # v7.3.0: 缺口块+双 skill 节较重，240s 早高峰三连超时
        job=job,
    )
    if not update.get("success"):
        return {"success": False, "error": update.get("error", "手册升级失败")}

    manual_path = prop_dir / "03_method" / "method-manual.md"
    manual_size_after = manual_path.stat().st_size if manual_path.exists() else 0

    # v7.3.0 过线判定（口径见 docstring）
    min_score = threshold.get("min_overall_score", 0.85)
    weak_dims = [
        k for k in MANUAL_DIM_KEYS
        if k in dim_scores and float(dim_scores[k]) < 0.70
    ]
    dims_partial, dims_present, _dims_missing = judge_dims_partial(
        "method_manual", dim_scores
    )
    section_passed = bool(
        score >= min_score
        and not gaps
        and not weak_dims
        and readiness_level >= MANUAL_READY_LEVEL
        and manual_size_after >= MANUAL_MIN_BYTES
    )

    # 入史 + section_passes（不覆盖 last_score/last_dim_scores——2 维异口径）
    prop_state = self._get_proposal_state(proposal_id)
    prop_state.setdefault("score_history", []).append({
        "round": round_num,
        "score": score,
        "dim_scores": dim_scores,
        "weakest_dim": self._get_weakest_dimension(dim_scores),
        "focus_section": "method_manual",
        "section_passed": section_passed,
        "issues_count": len(issues),
        "high_issues": sum(1 for i in issues if i.get("severity") == "high"),
        # v7.3.0 手册专属可观测字段：就绪度分级 / 升级动作数 / 手册体积
        "manual_readiness_level": readiness_level,
        "manual_bytes": manual_size_after,
        "manual_actions_applied": update.get("applied", 0),
        "caliber": "manual_2d",
        "dims_partial": dims_partial,
        "dims_present": dims_present,
        "anchor_conclusion": "",  # 手册为操作文档，语体锚点不适用（同 references）
        "at": now_utc(),
    })
    section_passes = prop_state.get("section_passes", {}) or {}
    section_passes["method_manual"] = section_passed
    prop_state["section_passes"] = section_passes
    prop_state["updated_at"] = now_utc()
    self._set_proposal_state(proposal_id, prop_state)

    if _log:
        _log.info(
            f"[{proposal_id}] 手册升级: score={score:.2f}, L{readiness_level}, "
            f"actions={update.get('applied', 0)}, passed={section_passed}"
        )
    return {
        "success": True,
        "score": score,
        "section_passed": section_passed,
        "readiness_level": readiness_level,
        "applied": update.get("applied", 0),
    }


# v7.3.32: 手册分节写入支撑（全部零 LLM、纯函数，可单测）。
_MANUAL_SOFT_CAP = 60000
_MANUAL_SECTION_CAP = 8000
_MANUAL_HEAD_RE = re.compile(r"#{2,4} ")


def _manual_head_level(line: str) -> int:
    """返回标题层级（##=2 … ####=4）；非标题返回 0。"""
    m = _MANUAL_HEAD_RE.match(line or "")
    return len(m.group(0)) - 1 if m else 0


def _manual_section_end(lines: List[str], start_idx: int) -> int:
    """返回该标题所在小节的结束行下标（0-based 开区间）。

    v7.3.33（BUG-42）修复：v7.3.32 的实现把「下一个任意级标题」当作节
    边界，导致父节的正文被 #### 子节提前截断——例如
    `### 2.11 目标一判据协议` 只拿到 L396-L403（333 字符），
    而它实际含 4 个 #### 子节共 7163 字符。后果有二：
      ① 目录里的字符数失真（§2.11 报 333 而实际 7163），planner
         按失真体量排动作优先级；
      ② 分节写入时 writer 只被授权改这 333 字符的父节标题+首段，
         真正要改的判据正文（#### 2.11.1~2.11.4）全在授权范围外，
         越界风险与"改了但没改到"的语义偏差同时出现。

    正确语义：节边界 = 下一个**同级或更高级**的标题（子标题属于本节）。
    """
    level = _manual_head_level(lines[start_idx])
    for k in range(start_idx + 1, len(lines)):
        lj = _manual_head_level(lines[k])
        if lj and lj <= level:
            return k
    return len(lines)


def _manual_toc(text: str) -> List[Dict[str, Any]]:
    """解析手册目录：每节标题 + 行范围（1-based 含端点）+ 字符数。

    v7.3.32: 阶段1 由「喂头部 4000 字符」改为「喂全量目录」——旧实现只让
    planner 看到前 4000 字符，大册中后部小节（如 §4）对计划不可见。
    v7.3.33（BUG-42）：节范围按「同级或更高级标题」切分，子节归属父节。
    """
    lines = (text or "").split("\n")
    heads = [i for i, l in enumerate(lines) if _MANUAL_HEAD_RE.match(l)]
    toc: List[Dict[str, Any]] = []
    for i in heads:
        end = _manual_section_end(lines, i)
        body = "\n".join(lines[i:end])
        toc.append({
            "title": lines[i].strip(),
            "start": i + 1,
            "end": end,
            "chars": len(body),
        })
    return toc


def _format_manual_toc(toc: List[Dict[str, Any]]) -> str:
    """目录 → prompt 文本（标题 / 行范围 / 字符数）。"""
    return "\n".join(
        f"- L{t['start']}-L{t['end']}（{t['chars']} 字符）{t['title']}" for t in toc
    )


def _manual_section_slice(text: str, section: str) -> Optional[Dict[str, Any]]:
    """按标题定位单节，返回 {start,end,body}（行号 1-based 含端点）；未命中 None。"""
    if not section:
        return None
    lines = (text or "").split("\n")
    idx = [i for i, l in enumerate(lines) if l.strip() == section.strip()]
    if not idx:
        # v7.3.32: 计划里的 section 常写成裸标题（"数据采集"），手册里是
        # "### 数据采集"——按去掉 # 前缀后的标题再匹配一次
        _target = re.sub(r"^#{2,4}\s*", "", section.strip())
        idx = [
            i for i, l in enumerate(lines)
            if _MANUAL_HEAD_RE.match(l)
            and re.sub(r"^#{2,4}\s*", "", l.strip()) == _target
        ]
    if not idx:
        return None
    i = idx[0]
    end = _manual_section_end(lines, i)
    return {"start": i + 1, "end": end, "body": "\n".join(lines[i:end])}


def _manual_section_brief(body: str, cap: int = _MANUAL_SECTION_CAP) -> str:
    """单节文本按上限裁剪：超限给首尾各半 + 省略提示（禁整册注入的兜底）。"""
    if len(body) <= cap:
        return body
    half = cap // 2
    return (
        f"{body[:half]}\n\n…（本节约 {len(body)} 字符，中段已省略；"
        f"只可在下述行范围内改写）…\n\n{body[-half:]}"
    )


def _manual_out_of_range(before: str, after: str, start: int, end: int) -> int:
    """行级 diff：统计目标节 L{start}-L{end} 之外被改动的行数（近似口径）。

    v7.3.32: 分节写入的可观测护栏——动作后比对前后全文，越界行数非零即
    记入返回值（不自动回滚，避免误伤合法的跨节指针修正）。
    """
    b = (before or "").split("\n")
    a = (after or "").split("\n")
    lo, hi = start - 1, end  # 0-based，hi 为开区间
    changed = 0
    sm = difflib.SequenceMatcher(None, b, a, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        if tag in ("replace", "delete"):
            changed += sum(1 for i in range(i1, i2) if not (lo <= i < hi))
        if tag in ("replace", "insert"):
            changed += sum(1 for j in range(j1, j2) if not (lo <= j <= hi))
    return changed


def _manual_two_phase_update(
    self,
    proposal_id: str,
    prop_dir: Path,
    plan_extra: str = "",
    max_actions: int = 4,
    skill_sections: tuple = ("一、更新纪律",),
    plan_note: str = "手册维护强制纪律",
    plan_timeout: int = 240,
    job: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """v7.3.0: 手册两阶段更新核心（规划→逐节执行），供两处复用：
    - derived 步 `_run_update_method_manual_step`（历史行为不变：无缺口注入）
    - 模块 writer 步 `_run_manual_writer_step`（critic 缺口驱动升级）

    两阶段机制沿用 v7.2.11：阶段1 只喂手册头部目录区 + 体积统计 + 方案
    节选，产出结构化更新计划 JSON；阶段2 每动作独立 hermes 会话，单动作
    失败跳过不拖垮整步。

    plan_timeout：阶段1超时（legacy 240s；手册模块版带缺口块 + 双 skill
    节，实测早高峰三连超时，v7.3.0 修复放宽到 480s）。

    v7.3.46: job 传入时阶段2 动作超时梯度化——v7.3.3 分级基线（add/revise
    300s、compress/merge 480s）在模型逃生备用链路（minimax-cn 高延迟）下
    连续砍尾（moire 实测 2 个 revise 300s 双超时），与
    `_step_hermes_timeout` 同款按重试次数放宽。
    """
    proposal_path = prop_dir / "04_proposal" / "proposal-draft.md"

    method_dir = prop_dir / "03_method"
    method_dir.mkdir(parents=True, exist_ok=True)
    manual_path = method_dir / "method-manual.md"

    # 优先读取 scheme 模块的 writer 输出，若不存在则读完整 draft
    # v7.3.27: 上游方案输入不再截断 8000 字符——houston 实证 scheme 20310
    # 字符，Jessen/Andersen 等判据位于 offset 11580/11939，writer 从未见过，
    # critic 却按全文核查 → 要素①"方案路线零落点"反复立案而 writer 无据可补。
    _SCHEME_INPUT_CAP = 30000
    scheme_path = prop_dir / "04_proposal" / "sections" / "scheme.md"
    if scheme_path.exists():
        method_source = scheme_path.read_text(encoding="utf-8")[:_SCHEME_INPUT_CAP]
    else:
        method_source = proposal_path.read_text(encoding="utf-8")[:_SCHEME_INPUT_CAP]

    manual_text = ""
    if manual_path.exists():
        try:
            manual_text = manual_path.read_text(encoding="utf-8")
        except Exception:
            manual_text = ""
    # v7.3.27: 体积口径修正——原实现用 stat().st_size（UTF-8 字节），却按
    # "字符"与 60000 上限比较：中文手册 ~3 字节/字，houston 40475 字符被报成
    # 65054"字符"，每轮凭空多出一个 compress 动作（6 动作预算被挤占 1 个）。
    _manual_size = len(manual_text)
    # v7.3.32: 阶段1 注入全量目录（标题+行范围+字符数），替代旧「头部 4000 字符」
    _toc = _manual_toc(manual_text)
    _toc_text = _format_manual_toc(_toc)

    # v7.3.27: 手册写入侧接入口径表（与 critic 侧同源）——canonical 值 +
    # 全册禁用旧值命中（带行号）。此前手册是唯一不入口径校验的产品文档，
    # writer 只能按 critic 点名行逐处打补丁（4.19 eV / 1.7×10⁷ 双版本滞留）。
    _params_block, _manual_hits_block = "", ""
    try:
        from .params_registry import (
            load_params,
            format_params_block,
            scan_manual_conflicts,
            format_manual_conflicts_block,
        )
        _pdata = load_params(prop_dir)
        if _pdata:
            _params_block = format_params_block(_pdata)
            _manual_hits_block = format_manual_conflicts_block(
                scan_manual_conflicts(prop_dir, _pdata)
            )
    except Exception:
        _params_block, _manual_hits_block = "", ""

    # 手册质量纪律收敛于 skill，两阶段均注入
    try:
        from skill_loader import inject_block
        _mm_skill = inject_block("method-manual", list(skill_sections), note=plan_note)
    except Exception:
        _mm_skill = ""

    # ============ 阶段1：更新计划（小输出、快会话） ============
    # v7.3.32: 移除「超限必含 compress 整册压缩」口径——超限只提示按节瘦身，
    # compress 仅用于该节内部跨节重复收口，禁止整册重写（用户裁决 2026-11-05）。
    _compress_req = ""
    if _manual_size > _MANUAL_SOFT_CAP:
        _compress_req = (
            f"■ 体积提示（当前 {_manual_size} 字符 > {_MANUAL_SOFT_CAP} 上限）：\n"
            f"- 计划按「单节瘦身」组织：只挑字符数最大的 1-2 个节各给一个 compress 动作，"
            f"禁止产出整册重写的动作。\n"
            f"- compress 仅用于该节内部的跨节重复收口（同一结论保留一处权威表述、"
            f"其余改为指回章节），目标单节 ≤ 原节 70%；数值、判据条目、协议步骤、"
            f"[[链接]] 与失效模式条数一条不得减少。\n\n"
        )

    plan_prompt = (
        f"请为方法学手册制定本轮更新计划（只输出计划，不写手册文件）。\n\n"
        f"【手册现状】\n"
        f"- 路径：{manual_path}\n"
        f"- 体积：{_manual_size} 字符\n"
        f"- 目录（共 {len(_toc)} 节，标题 / 行范围 / 字符数）：\n"
        f"{_toc_text or '（手册尚不存在，首轮创建）'}\n\n"
        f"【本轮方案内容（研究方案节选）】\n{method_source}\n\n"
        f"{_params_block}"
        f"{_manual_hits_block}"
        f"{_compress_req}"
        f"{plan_extra}"
        f"{_mm_skill}\n"
        f"【输出格式】严格输出一个 JSON 对象（不要其它文字）：\n"
        f'{{"actions": [{{"action": "compress|merge|revise|add", '
        f'"section": "小节标题（新小节用拟新增标题）", '
        f'"detail": "一句话说明改什么", '
        f'"source_hint": "相关知识库方法页名（可空）"}}]}}\n\n'
        f"要求：\n"
        f"1. 最多 {max_actions} 个动作，按优先级排序（超上限时 compress 最优先）\n"
        f"2. 每个动作只针对一个小节，粒度要小到单会话可完成\n"
        f"3. 方案新引入的方法细节优先 add/revise；语义重复的用 merge；超上限用 compress\n"
        f"4. 可参考 knowledge/wiki/methods/ 文件名索引挑选 source_hint\n"
        f"5. 口径旧值必须清零：上文「手册口径旧值命中」中的每一条都要有动作覆盖，\n"
        f"   同一旧值落在多个小节时按小节归并（一个节一个 revise），不得只改点名行\n"
    )
    # v7.2.11: 阶段1只做规划，输出小；超时经 plan_timeout 参数化
    # （legacy 240s；v7.3.0 手册模块版 480s，见 docstring）
    plan_result = self._run_hermes("writer", plan_prompt, timeout=plan_timeout)
    if not plan_result.get("success"):
        return {"success": False, "error": f"阶段1规划失败: {plan_result.get('error', '未知')}"}

    # 解析计划 JSON（容忍 markdown 代码块包裹）
    plan_text = plan_result.get("output", "")
    actions = self._parse_manual_plan(plan_text)
    if actions is None:
        return {"success": False, "error": f"阶段1计划解析失败: {plan_text[:200]}"}

    # 计划落盘（审计与下一轮对照）
    plan_path = method_dir / "manual-update-plan.md"
    try:
        plan_lines = [f"# 手册更新计划（{now_utc()}，v7.2.11 两阶段）", ""]
        for i, a in enumerate(actions, 1):
            plan_lines.append(
                f"{i}. [{a.get('action', '?')}] {a.get('section', '?')}"
                f" — {a.get('detail', '')}"
                f"（source: {a.get('source_hint', '') or '-'}）"
            )
        plan_path.write_text("\n".join(plan_lines) + "\n", encoding="utf-8")
    except Exception:
        pass

    if not actions:
        # 空计划 = 本轮无需更新（合法：方案无新方法细节且未超上限）
        if _log:
            _log.info(f"[{proposal_id}] method-manual 阶段1空计划，本轮跳过更新")
        return {"success": True, "manual_path": str(manual_path),
                "plan_path": str(plan_path), "applied": 0, "skipped_reason": "empty_plan"}

    # ============ 阶段2：逐节执行（每动作独立小会话） ============
    applied, failed_actions, out_of_range_total = 0, [], 0
    _live_text = manual_text
    for a in actions[:max_actions]:
        act = str(a.get("action", "revise"))
        section = str(a.get("section", "")).strip()
        if not section:
            continue
        detail = str(a.get("detail", ""))
        source_hint = str(a.get("source_hint", "") or "").strip()
        _src_line = ""
        if source_hint and act in ("add", "revise"):
            _src_line = (
                f"- 参数溯源：优先读 knowledge/wiki/methods/{source_hint}.md"
                f"（不存在则按文件名索引另选相关页），适用方法与参数按来源并入。\n"
            )
        _act_desc = {
            "compress": f"压缩合并小节「{section}」：合并语义重复/过时条目，精简表述（目标单节 ≤8000 字符）",
            "merge": f"将小节「{section}」与语义重复的小节合并为一个，保留最完整表述",
            "revise": f"修订小节「{section}」：{detail}",
            "add": f"新增小节「{section}」：{detail}",
        }.get(act, f"处理小节「{section}」：{detail}")

        # v7.3.32: 分节写入——注入目标节行范围与原文，明令只替换该范围
        _sl = _manual_section_slice(_live_text, section)
        if _sl:
            _range_line = (
                f"- 目标节行范围：L{_sl['start']}–L{_sl['end']}"
                f"（{len(_sl['body'])} 字符）\n"
            )
            _body_block = (
                f"【目标节现状（原文，仅此节）】\n{_manual_section_brief(_sl['body'])}\n\n"
                f"【写入边界（强制）】\n"
                f"- 只允许替换 L{_sl['start']}–L{_sl['end']} 这一节的内容；"
                f"该范围以外的任何行必须原样保留。\n"
                f"- 禁止整册重写、禁止重新排版全册、禁止改动其它小节。\n"
                f"- 若需修正其它节的指针，改写为在本节内指回该节（不改对方正文）。\n\n"
            )
        else:
            _range_line = f"- 目标节尚不存在（{act}）：追加到主题最相近小节之后\n"
            _body_block = ""

        exec_prompt = (
            f"请对方法学手册执行一个小节级更新（只处理下述一个小节，不动其它部分）。\n\n"
            f"手册路径：{manual_path}\n{_range_line}\n"
            f"【任务】\n{_act_desc}\n"
            f"{_src_line}"
            f"\n【执行纪律】\n"
            f"1. 按标题「{section}」在手册中定位（新小节追加到最相近主题之后；手册不存在则创建并写入该小节）\n"
            f"2. 只读写该小节附近内容，不必通读全册\n"
            f"3. 直接改写文件，保持其余小节原样\n"
            f"4. 方法细节含：算法/实验步骤、关键参数（带单位）、验证方式、风险与替代方案\n"
            f"5. KB 引用落地（v7.3.3）：本节取材自知识库方法页/论文方法卡的参数与细节，"
            f"须以 [[methods/<slug>]] / [[papers/<slug>]] 节点标注来源（slug 与素材包一致）——"
            f"这是手册溯源闭环（八要素⑧）的机器可校验形态\n"
            f"6. 瘦身不得减项（v7.3.32）：压缩时数值/单位、判据条目、协议步骤、[[链接]]、"
            f"失效模式条数一律不得减少；删掉的叙述须在本节内保留权威表述并指回章节\n\n"
            f"{_body_block}"
            f"{_mm_skill}\n"
            f"{_params_block}"
            f"{_manual_hits_block}"
            f"【本轮方案依据（节选）】\n{method_source[:8000]}\n"
        )
        # v7.3.3: 按动作类型分级超时——compress/merge 需通读并重写大段
        # （bsv 66KB 全册压缩 300s 三连超时实录），add/revise 单小节 300s 足够
        # v7.3.46: 重试时梯度放宽（备用模型高延迟尾部，moire 实测双超时）
        _exec_timeout = _step_hermes_timeout(
            job, 480 if act in ("compress", "merge") else 300
        )
        exec_result = self._run_hermes("writer", exec_prompt, timeout=_exec_timeout)
        if exec_result.get("success"):
            applied += 1
            # v7.3.32: 动作后行级 diff——越界改动计数（不自动回滚）
            try:
                _after_text = manual_path.read_text(encoding="utf-8") if manual_path.exists() else ""
                if _sl and _after_text:
                    _oor = _manual_out_of_range(
                        _live_text, _after_text, _sl["start"], _sl["end"]
                    )
                    out_of_range_total += _oor
                    if _oor and _log:
                        _log.warning(
                            f"[{proposal_id}] method-manual 动作越界改动 "
                            f"{_oor} 行（{act}:{section[:30]}，"
                            f"目标 L{_sl['start']}-L{_sl['end']}）"
                        )
                _live_text = _after_text or _live_text
            except Exception:
                pass
        else:
            failed_actions.append(f"{act}:{section}")
            if _log:
                _log.warning(
                    f"[{proposal_id}] method-manual 阶段2动作失败"
                    f"（{act}:{section[:40]}）: {exec_result.get('error', '')[:120]}"
                )

    if applied == 0:
        return {
            "success": False,
            "error": f"阶段2全部动作失败: {','.join(failed_actions[:3])}",
            "plan_path": str(plan_path),
        }
    if failed_actions:
        if _log:
            _log.info(
                f"[{proposal_id}] method-manual 阶段2部分成功 "
                f"{applied}/{len(actions[:max_actions])}，失败: {failed_actions}"
            )
    # v6.10.41: 事后膨胀检测（>10% 记 warning）
    # v7.3.27: 前后口径统一为字符数（原先 after 用字节 vs before 用字符，
    # 中文手册必然触发假膨胀告警）
    remaining_stale = 0
    try:
        _after_size = len(manual_path.read_text(encoding="utf-8")) if manual_path.exists() else 0
        if _manual_size and _after_size > _manual_size * 1.10:
            if _log:
                _log.warning(
                    f"[{proposal_id}] method-manual 本轮膨胀 "
                    f"{_after_size - _manual_size} 字符"
                    f"（{_manual_size}→{_after_size}），超出 10% 阈值"
                )
    except Exception:
        pass
    # v7.3.27: 动作后零 LLM 复检——口径旧值仍有残留则在返回值里显式计数，
    # 供下一轮计划继续覆盖（不自动改写，避免改坏"已撤销"类历史表述语义）
    try:
        from .params_registry import load_params, scan_manual_conflicts
        _pdata2 = load_params(prop_dir)
        if _pdata2 and manual_path.exists():
            remaining_stale = len(scan_manual_conflicts(prop_dir, _pdata2))
            if remaining_stale and _log:
                _log.info(
                    f"[{proposal_id}] method-manual 动作后仍有 {remaining_stale} "
                    f"处口径旧值命中（下一轮计划须继续覆盖）"
                )
    except Exception:
        remaining_stale = 0
    return {"success": True, "manual_path": str(manual_path),
            "plan_path": str(plan_path), "applied": applied,
            "remaining_stale": remaining_stale,
            "out_of_range": out_of_range_total}


def _run_update_method_manual_step(self, proposal_id: str, job: Dict[str, Any]) -> Dict[str, Any]:
    """v6.8.0: 根据申请书更新方法学手册，在方法层面补充细节。

    v7.2.11: 拆两阶段生成——旧实现单次 hermes 会话读全册（实测 60-186KB）
    + 压缩合并 + 写回，qgi r1 与 attosecond r1 双双 600s 超时（手册读写
    量远超单会话负载）。
    v7.3.0: 建轮链已撤除本 derived 步（手册由 method_manual 模块的
    critic→writer 对抗链接管）。本入口保留给历史遗留 job 与手动 CLI
    调用，行为与 v7.2.11 完全一致——两阶段核心已抽至
    _manual_two_phase_update（与模块 writer 步共享；经模块级函数直调
    而非 self 属性查找，MagicMock self 下不被自动 mock 短路）。
    """
    prop_dir = self._find_proposal_dir(proposal_id)
    if not prop_dir:
        return {"success": False, "error": "proposal 目录不存在"}

    proposal_path = prop_dir / "04_proposal" / "proposal-draft.md"
    if not proposal_path.exists():
        return {"success": False, "error": "申请书不存在"}

    return _manual_two_phase_update(
        self,
        proposal_id, prop_dir,
        plan_extra="",
        max_actions=4,
        skill_sections=("一、更新纪律",),
        plan_note="手册维护强制纪律",
        job=job,
    )


def _parse_manual_plan(self, plan_text: str) -> Optional[List[Dict[str, Any]]]:
    """v7.2.11: 解析阶段1输出的更新计划 JSON。

    容忍 markdown 代码块包裹与前后杂文；返回动作列表（可能为空列表），
    解析失败返回 None（与"合法空计划"区分）。

    v7.3.45 容错强化（moire 实测：writer 输出前导推理 + JSON 串内含
    换行/引号时旧解析器 3 连败卡死课题）：
    1. 平衡扫描替代非贪婪正则——代码围栏内取「首个 { 到与之配平的 }」，
       避免嵌套对象被 `\{.*?\}` 截断或尾围栏缺失时取到半截 JSON；
    2. 修复通道——字符串字面量内的裸换行/制表符转义、尾逗号剔除；
    3. 兜底打捞——逐字段正则提取 action/section/detail/source_hint
       重组计划（JSON 完全不可解析但字段文本在场时仍可推进）。
    """
    import re as _re
    if not plan_text or not plan_text.strip():
        return None
    text = plan_text.strip()

    def _balanced_json(candidate: str) -> Optional[str]:
        """从 candidate 中取首个配平的顶层 JSON 对象文本（容忍围栏/杂文）。"""
        s = candidate.find("{")
        if s == -1:
            return None
        depth = 0
        in_str = False
        esc = False
        for i in range(s, len(candidate)):
            ch = candidate[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return candidate[s:i + 1]
        return None

    def _repair_json(fragment: str) -> str:
        """常见 LLM JSON 修复：串内裸控制字符转义 + 尾逗号剔除。"""
        out = []
        in_str = False
        esc = False
        for ch in fragment:
            if in_str:
                if esc:
                    esc = False
                    out.append(ch)
                    continue
                if ch == "\\":
                    esc = True
                    out.append(ch)
                    continue
                if ch == '"':
                    in_str = False
                    out.append(ch)
                    continue
                if ch == "\n":
                    out.append("\\n")
                    continue
                if ch == "\t":
                    out.append("\\t")
                    continue
                if ch == "\r":
                    continue
                out.append(ch)
                continue
            if ch == '"':
                in_str = True
                out.append(ch)
                continue
            out.append(ch)
        return _re.sub(r",\s*([}\]])", r"\1", "".join(out))

    def _loads_any(fragment: str) -> Optional[dict]:
        for candidate in (fragment, _repair_json(fragment)):
            try:
                obj = json.loads(candidate)
                if isinstance(obj, dict):
                    return obj
            except Exception:
                continue
        return None

    obj = None
    # 优先：代码围栏内的 JSON（可能存在多个围栏块，取含 "actions" 的）
    for m in _re.finditer(r"```(?:json)?\s*(.*?)```", text, _re.DOTALL):
        frag = _balanced_json(m.group(1)) or ""
        obj = _loads_any(frag) if frag else None
        if obj and isinstance(obj.get("actions"), list):
            break
    # 次选：全文首个配平对象（无围栏或围栏未闭合）
    if obj is None or not isinstance(obj.get("actions"), list):
        frag = _balanced_json(text)
        if frag:
            obj = _loads_any(frag) or obj

    actions = obj.get("actions") if isinstance(obj, dict) else None

    # 兜底打捞：字段级正则重组（action 与 section 同对象邻接出现）
    if not isinstance(actions, list):
        actions = []
        for am in _re.finditer(
            r'"action"\s*:\s*"(add|revise|merge|compress)"[^{}]*?'
            r'"section"\s*:\s*"([^"]+)"', text, _re.DOTALL
        ):
            chunk = am.group(0)
            dm = _re.search(r'"detail"\s*:\s*"([^"]*)"', chunk)
            sm = _re.search(r'"source_hint"\s*:\s*"([^"]*)"', text[am.start():am.start() + 600])
            actions.append({
                "action": am.group(1),
                "section": am.group(2),
                "detail": dm.group(1) if dm else "",
                "source_hint": sm.group(1) if sm else "",
            })
        if not actions:
            return None

    valid = []
    for a in actions:
        if isinstance(a, dict) and a.get("section"):
            valid.append({
                "action": str(a.get("action", "revise")),
                "section": str(a.get("section", "")),
                "detail": str(a.get("detail", "")),
                "source_hint": str(a.get("source_hint", "") or ""),
            })
    return valid[:8]


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

    # v6.9.62: 残缺维度轮跳过 agent 奖惩（对齐 v6.8.48 解析失败不误扣
    # 模式）——critic 维度缺失时分数是残缺口径，据此加减 agent 分会误奖误罚。
    # v7.2.41 BUG-8：期望集改为口径感知（章节 4 维 / references 2 维），
    # 否则正文轮恒被判残缺 → 全部正文轮的 writer/critic 奖惩被静默清零。
    # v7.2.42 BUG-9：monitor job 的 section_key 是伪章节 "monitor"（不在
    # PROPOSAL_SECTIONS 中），且其 depends_on 恒为 references-writer
    # （controller.py:415 建轮不变量），评判对象实为 references 专轮。
    # v7.2.41 口径感知改造后 "monitor" 落入 else 分支取章节 4 维期望，
    # 而读盘又回退到裸路径 critic-round-{n}.md（references 2 维报告占用）
    # → 期望 4 维 / 实得 2 维 → dims_partial 恒 True → agent 奖惩 100%
    # 被跳过（实测全库 20/20 monitor 轮）。此处显式把 monitor 归一到
    # references 口径，与 depends_on 的真实评判对象一致。
    _caliber_key = caliber_dim_key(section_key)
    _critic_dims = (self._read_critic_report(prop_dir, round_num, _caliber_key).get("dim_scores") or {})
    _dims_partial, _dp_present, _dp_missing = judge_dims_partial(
        _caliber_key, _critic_dims
    )
    if _dims_partial:
        if _log:
            _log.warning(
                f"[{proposal_id}] r{round_num} {section_key} 维度残缺，"
                f"跳过 agent 奖惩（残缺口径不参与分数调整）"
            )
        # 零增量（record_monitor_history 按 dict 取键，不可传 None）
        deltas = {"writer_delta": 0, "critic_delta": 0, "skipped_partial_dims": True}
    else:
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
    # v7.2.0: 可执行性独立信号顶层快照（0 = 未评估），看板/dossier 直接读
    prop_state["last_executability_score"] = monitor_result.get("executability_score", 0.0)
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
        # v6.10.3 F2: 晋级方式打标——区分"真达标晋级"（all_sections_passed）
        # 与"逃生阀晋级"（escape_max_rounds / escape_no_improvement /
        # quality_declining）。待审队列据此分组，防止逃生阀课题以
        # 达标观感混入（实测 attosecond：references 口径 0.85 豁免警告，
        # 1/5 模块通过无标注进队）。
        promotion_kind = done_result.get("promotion_kind") or "unknown"
        prop_state = self._get_proposal_state(proposal_id)
        if prop_state:
            if quality_warning:
                prop_state["quality_warning"] = quality_warning
            prop_state["promotion_kind"] = promotion_kind
            self._set_proposal_state(proposal_id, prop_state)
            if quality_warning and _log:
                _log.warning(f"[{proposal_id}] {quality_warning}")
            if _log:
                _log.info(f"[{proposal_id}] 晋级方式: {promotion_kind}")
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

    # v7.3.48: 派活前写作并发守卫——`.write-lock` 存在且持有者不是本 job 时
    # 跳过并记录，不抢写（fail-open，锁模块异常不阻塞调度）。
    _prop_dir_guard = self._find_proposal_dir(proposal_id)
    if _prop_dir_guard:
        try:
            from lifecycle.write_guard import check_write_lock
            _ok, _why = check_write_lock(_prop_dir_guard, f"job:{job['job_id']}")
            if not _ok:
                if _log:
                    _log.warning(f"[{proposal_id}] 跳过 {step}: {_why}")
                return {"success": False, "skipped": "write_lock_held",
                        "error": _why, "executed": False}
        except Exception as e:
            if _log:
                _log.warning(f"[{proposal_id}] 写锁检查异常（按无锁继续）: {e}")

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
    job["_run_started_at"] = now_utc()

    t0 = time.time()
    # v7.3.0: method_manual 模块的 critic/writer 走专用步（手册产物在
    # 03_method/，不在 04_proposal/sections/，通用章节步的文件机制不适用）
    _manual_step = job.get("section_key") == "method_manual"
    try:
        if step == STEP_CRITIC:
            result = (
                self._run_manual_critic_step(proposal_id, job) if _manual_step
                else self._run_critic_step(proposal_id, job)
            )
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
            result = (
                self._run_manual_writer_step(proposal_id, job) if _manual_step
                else self._run_writer_step(proposal_id, job)
            )
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

    # v7.3.48: writer 落盘后写作并发守卫——登记写入、10 分钟内同章节 ≥2 写入者
    # 自动冻结；并复核历史 round-N 报告存证哈希，不一致改名 stale（不覆盖）。
    if result.get("success") and step == STEP_WRITER and _prop_dir_guard:
        try:
            from lifecycle.write_guard import record_section_write, mark_stale_reports
            _skey = job.get("section_key") or ""
            _rec = record_section_write(_prop_dir_guard, _skey, f"job:{job['job_id']}")
            if _rec.get("conflict"):
                _st = self._get_proposal_state(proposal_id) or {}
                _st["scheduler_frozen"] = True
                _st["scheduler_frozen_reason"] = f"写冲突自动冻结：{_rec['reason']}"
                self._set_proposal_state(proposal_id, _st)
                if _log:
                    _log.warning(
                        f"[{proposal_id}] 写冲突自动冻结（{_skey}）: {_rec['reason']}"
                    )
            # v7.3.52 BUG-47a 修复：传入本轮轮次——本轮 critic 报告的存证
            # 哈希本就应与「writer 改后的正文」不同，若一并改名，本轮报告
            # 会被 executor._read_critic_report 按精确名读成空 → 该章节
            # 后续 score/dim_scores 全失真。只对历史轮次做陈旧判定。
            _stale = mark_stale_reports(
                _prop_dir_guard, _skey, _rec.get("sha256"),
                current_round=round_num,
            )
            if _stale.get("stale") and _log:
                _log.warning(
                    f"[{proposal_id}] {_skey} 正文已变，{len(_stale['stale'])} 份旧报告"
                    f"标记 stale: {', '.join(_stale['stale'])}"
                )
        except Exception as e:
            if _log:
                _log.warning(f"[{proposal_id}] 写后守卫异常（忽略）: {e}")

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

    # v6.9.82: worker 入口派发前检查熔断器——open/probing 停摆期间
    # worker cron 不应绕过止血继续派活（微调度器路径 v6.8.50 起已有
    # 该检查，worker 路径此前缺失）。温和退出不报错，等冷却/试探自愈。
    try:
        from circuit_breaker import allow_dispatch as cb_allow
        if not cb_allow():
            return {"success": True, "reason": "熔断器 open/probing，跳过本轮",
                    "executed": False, "skipped": "circuit_open"}
    except Exception:
        pass

    with file_lock(f"proposal-{proposal_id}"):
        job = self.pick_next_job(proposal_id)
        if not job:
            return {"success": True, "reason": "无待执行 job", "executed": False}
        result = self.execute_job(job)
        result["executed"] = not result.get("skipped")
        result["job_id"] = job["job_id"]
        # v6.9.82: worker 入口补熔断回报——与微调度器路径相同四元组。
        # 此前该路径执行后不回报 record_job_result，失败不计入分桶/
        # 长链计数：若 worker cron 承接时段执行（微调度器停摆/锁忙时），
        # critic 连续挂起将无法触发模型逃生，白烧整个时段。幂等无害：
        # job 终态后另一入口 pick 不到同一 job，不会双计。
        try:
            from circuit_breaker import record_job_result as cb_record, LONG_OUTPUT_STEPS
            _step = job.get("step", "")
            cb_record(
                result.get("success", False),
                result.get("error", ""),
                job_kind="long" if _step in LONG_OUTPUT_STEPS else "short",
                step=_step,
            )
        except Exception as e:
            if _log:
                _log.warning(f"[worker] 熔断器回报异常（忽略）: {e}")
        return result
