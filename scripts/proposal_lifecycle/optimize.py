from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import os
import re
import subprocess

from common import now_utc, load_json, hermes_subprocess_env

import proposal_lifecycle as _pl

from proposal_sections import ProposalSections, PROPOSAL_SECTIONS

from proposal_lifecycle.constants import (
    _log,
    DEFAULT_MAX_ROUNDS,
    DEFAULT_SCORE_THRESHOLD,
)

# v7.3.41: A 通道收分口径拆分——判定用 cap 前原始四维加权分，
# 展示仍用 cap 后综合分（开关 LINSAI_A_GATE_RAW_SCORE 默认 on）
from proposal_lifecycle.a_gate import calibers as _a_gate_calibers

# v6.9.53: 章节卫生——体量参考 / full_review 纯净性预检 / 质量缺陷指令
# v6.9.55: 质量核心——writer 指令从"净删 N 字"（字数是症状）改为
# 具体缺陷位置（冗余句/无关段——病因），字数降为上下文信号。
from proposal_lifecycle.section_hygiene import (
    budget_report_text,
    full_review_purity_text,
    quality_directives_text,
)

# v6.8.6: 范本写作标杆已提炼嵌入 nsfc-standards.json 的
# reference_materials.style_benchmark 字段，agent 读 JSON 即可获取全部规则，
# 无需每次读原始范本文件（节省 ~29KB token/次）。


# ---------------------------------------------------------------------------
# v6.8.46: hermes API 错误检测
#   配额耗尽/限流/网关故障时，hermes CLI 以 returncode=0 退出，
#   stdout 为错误文本。该文本进入评审解析链会产生伪分数
#   （2026-08-14 实例：MiniMax 429 文本被解析为 0.18 综合分）。
#   短输出（<2000 字符）中命中任一特征即判为 API 错误。
# ---------------------------------------------------------------------------
_API_ERROR_SIGNATURES = (
    "API call failed",
    "已达到 Token Plan 用量上限",
    "购买积分补充用量",
    "HTTP 429",
    "rate limit exceeded",
    "quota exceeded",
    "insufficient_quota",
    "API 调用失败",
    "余额不足",
    "账户已欠费",
)


def _detect_api_error(output: str) -> str:
    """检测 hermes stdout 是否为 API 错误文本。

    Returns:
        命中的错误特征（用于日志与 error 字段）；正常输出返回空字符串。
    """
    if not output:
        return ""
    # 错误文本通常很短；正常评审输出动辄上万字符，
    # 长输出中偶尔引用错误信息不应误判
    if len(output) > 2000:
        return ""
    for sig in _API_ERROR_SIGNATURES:
        if sig in output:
            return sig
    return ""


# v6.9.84→v6.9.85: 挂起击杀窗口。0 = 禁用（默认）。
# 教训（09-01 实证）：hermes CLI -z 模式工作期间完全静默——55s 执行的
# 真实调用全程零输出，仅在完成时一次性输出到 stdout；stderr 亦静默。
# v6.9.84 的"持续产出=在干活"前提不成立，360s 零输出击杀误杀了所有
# 超过 6 分钟的正常任务（08-31 晚~09-01 晨 critic 12 连挂，0 成功，
# 含备用模型上的正常任务）。CLI 模式下不存在可靠的中间活性信号，
# 暂时禁用 stall 击杀；框架保留，待 hermes 提供心跳/进度输出后再启用。
HERMES_STALL_TIMEOUT_S = 0


def _communicate_with_stall(
    proc: "subprocess.Popen",
    timeout: float,
    stall_timeout: float = HERMES_STALL_TIMEOUT_S,
) -> Dict[str, Any]:
    """活性感知版 communicate：区分"慢而在跑"与"零输出挂起"。

    监测子进程 stdout/stderr 的输出活动：
    - 持续有产出 → 一直等到硬上限 timeout（慢任务不被砍）
    - 零输出超过 stall_timeout → 立即击杀（挂起快速失败）
    - 进程正常退出 → 吸干管道返回

    v6.9.85: stall_timeout 默认 0 = 禁用（hermes CLI 工作期间静默，
    管道零输出不代表挂起，详见 HERMES_STALL_TIMEOUT_S 注释）。仅当
    显式传入正值时生效（测试/将来 hermes 提供心跳输出后启用）。

    进程组击杀语义与旧实现一致（v6.8.3-fix9：SIGTERM → 5s → SIGKILL）。

    Returns:
        {"stdout": str, "stderr": str, "reason": "", "timeout": bool,
         "stall": bool, "stall_seconds": int, "elapsed_s": float}
    """
    import selectors
    import signal
    import time as _time

    t0 = _time.time()
    last_activity = t0
    out_buf: list = []
    err_buf: list = []
    out_fd = proc.stdout.fileno() if proc.stdout else -1
    err_fd = proc.stderr.fileno() if proc.stderr else -1
    sel = selectors.DefaultSelector()
    if out_fd >= 0:
        sel.register(proc.stdout, selectors.EVENT_READ)
    if err_fd >= 0:
        sel.register(proc.stderr, selectors.EVENT_READ)

    reason = ""
    timed_out = False
    stalled = False
    stall_seconds = 0
    try:
        while True:
            if proc.poll() is not None:
                break
            events = sel.select(timeout=1.0)
            got_data = False
            for key, _mask in events:
                try:
                    chunk = os.read(key.fd, 65536)
                except (BlockingIOError, InterruptedError, OSError):
                    continue
                if chunk:
                    if key.fd == out_fd:
                        out_buf.append(chunk)
                    else:
                        err_buf.append(chunk)
                    got_data = True
            now = _time.time()
            if got_data:
                last_activity = now
                continue
            if stall_timeout > 0 and now - last_activity >= stall_timeout:
                stalled = True
                stall_seconds = int(now - last_activity)
                reason = "stall"
                break
            if now - t0 >= timeout:
                timed_out = True
                reason = "timeout"
                break
    finally:
        sel.close()

    # 击杀（若仍在运行）：进程组整体清理
    if proc.poll() is None:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                proc.wait(timeout=3)
        except (ProcessLookupError, PermissionError):
            pass
    else:
        proc.wait()

    # 吸干管道残留（击杀后管道中可能仍有已写入数据）
    for fd, buf in ((out_fd, out_buf), (err_fd, err_buf)):
        if fd < 0:
            continue
        try:
            while True:
                chunk = os.read(fd, 65536)
                if not chunk:
                    break
                buf.append(chunk)
        except (BlockingIOError, InterruptedError, OSError):
            break
    try:
        proc.stdout.close()
        proc.stderr.close()
    except Exception:
        pass

    return {
        "stdout": b"".join(out_buf).decode("utf-8", errors="replace"),
        "stderr": b"".join(err_buf).decode("utf-8", errors="replace"),
        "reason": reason,
        "timeout": timed_out,
        "stall": stalled,
        "stall_seconds": stall_seconds,
        "elapsed_s": round(_time.time() - t0, 2),
    }


def _load_nsfc_writing_skill_text(role: str = "writer") -> str:
    """v7.0.0: 加载 nsfc-writing 写作纪律 skill（统一 skill_loader 通道）。

    v6.10.52 首发 / v7.0.0 重构：skill 真相源迁移到 .hermes/skills/
    nsfc-writing/SKILL.md（hermes 项目本地 trusted 目录，agent 会话自动
    进 skills index），并收编此前 optimize.py 硬编码的三处真相源
    （critic narrative_rules / writer narrative_requirement / purity 纪律）。
    本函数经 skill_loader 按角色裁剪注入核心红线，完整 skill 给路径由
    agent 按需深读。

    role="writer"：叙事主线纪律（二）+ 禁用词映射（三）+ 叙述规范（四）
                  + AI 模式修复（八）+ 自检提示
    role="critic"：叙述规范（四）+ AI 修复（八）+ critic 检查项（十）
                  + 禁用词映射（三）
    role="purity"：文件纯净性与内容边界（六）+ 内容质量纪律（七）
    fail-open：skill 缺失返回空串，不阻塞管线。
    """
    try:
        from skill_loader import inject_block, skill_path
    except Exception:
        return ""
    if role == "critic":
        return inject_block(
            "nsfc-writing",
            ["四、叙述式写作规范", "八、AI 写作模式修复", "十、critic 检查项",
             "三、禁用词与替换映射"],
            note="评审扣分依据；科学正确性优先级高于风格检查，本清单只约束表达方式",
            extra=(
                "凡是发现上述问题，必须标记 severity 和 issue_type，并给出"
                "具体改写建议。"
            ),
        )
    if role == "purity":
        return inject_block(
            "nsfc-writing",
            ["六、文件纯净性与内容边界", "七、内容质量纪律"],
            note="程序守卫强制，违反即返工",
        )
    return inject_block(
        "nsfc-writing",
        ["二、叙事主线纪律", "三、禁用词与替换映射", "四、叙述式写作规范",
         "八、AI 写作模式修复"],
        note="写作时强制执行，写完按 skill 九节自检清单逐项自查",
        extra=(
            "■ 修订现有章节时同样适用：逐段检查防御性内容密度与交叉引用"
            "预算，超标段落按二节降权重写，不新增防御性表述。"
        ),
    )


def _critic_report_path(prop_dir: Path, round_num: int, section_key: Optional[str] = None) -> Path:
    """v6.10.26: 对抗评审报告路径解析——按 section 分文件，杜绝同轮覆盖。

    旧约定所有 section 共用 `critic-round-{n}.md`，同一轮内 rationale/content/
    scheme/full_review/references 五个 job 写同一路径，后写覆盖先写；评审团
    （手动深度修改）落盘 `critic-round-{n}-{section}.md` 后缀报告后，裸文件
    被 references 2 维报告占用，executor 读裸文件算出章节轮伪分（实测
    attosecond r5 rationale=0.66=(0.60+0.72)/2，恰为 references 2 维均值）。

    新约定：传 section_key 时返回 `critic-round-{n}-{section_key}.md`（与
    评审团后缀格式一致，同轮多 section 不再互覆）；不传时返回裸路径
    （兼容 full_review 旧约定与历史裸文件读取）。
    """
    if section_key:
        return prop_dir / "05_review" / f"critic-round-{round_num}-{section_key}.md"
    return prop_dir / "05_review" / f"critic-round-{round_num}.md"


# v6.10.31: 多源检索配置——researcher 定向检索的源与年份口径（纯函数供回归）
_MULTI_SOURCE_SOURCES = ("arxiv", "openalex", "semantic_scholar")
_REFERENCES_FRESH_YEARS = 3


def _multi_source_search_config(
    focus_section: Optional[Dict[str, str]],
) -> tuple:
    """按聚焦章节返回 (sources, year_from)。

    - references / full_review 轮：year_from = 当前年 - 3——呼应
      references critic 检查项"总数 20-40 篇 + 是否包含近 3 年文献"，
      时效性缺口直接消解在检索源头上。注：job 链中 references 轮本身
      无 lit_search job（仅 critic+writer），full_review 轮的检索才是
      references 时效补充的实际载体，故两者都限年；经典文献由不限年
      的 hermes agent loop 检索层提供，多源层专注补新。
    - 其余章节/整篇轮：year_from = None——立项依据/机制溯源常需
      经典高引文献（如 Berry 1984），一刀切限年会误杀奠基性引用。
    - 源：三源并发（search_academic v6.10.31 并发化后墙钟不增加，
      semantic_scholar 匿名 429 由单源容错兜底，失败不拖垮聚合）。
    """
    if focus_section and focus_section.get("key") in ("references", "full_review"):
        from datetime import datetime, timezone as _tz
        year_from = datetime.now(_tz.utc).year - _REFERENCES_FRESH_YEARS
        return _MULTI_SOURCE_SOURCES, year_from
    return _MULTI_SOURCE_SOURCES, None


class OptimizeMixin:
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
        critic_timeout: int = 600,
        writer_timeout: int = 900,
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
        # v6.8.16 改进4: 维度轮换——连续 3 轮在同一维度原地踏步则跳过
        # v6.8.24 修复: 旧版窗口 [-6:] 在 5-section 轮转下同 section 最多出现 2 次，
        # 阈值 3 永远不可达。改为 [-12:]（覆盖 2+ 个完整轮转周期）。
        # v6.9.58 修复: [-12:] 仍是算术错误——周期 = len(SECTIONS)+1 = 6 轮，
        # 12 轮窗口同 section 最多 2 次，>=3 依旧不可达（实测维度轮换
        # 0 触发 0 记录）。窗口改 [-18:]（3 个完整周期），同 section 出现
        # 3 次的条件从 r12 起可达。
        section_cycle = current_round % (len(PROPOSAL_SECTIONS) + 1)
        if section_cycle < len(PROPOSAL_SECTIONS):
            focus_section = PROPOSAL_SECTIONS[section_cycle]
            is_full_review = False
            # 检查该维度是否连续 3 轮无提升
            score_history = prop_state.get("score_history", [])
            if len(score_history) >= 6:
                same_section_rounds = [
                    h for h in score_history[-18:]
                    if h.get("focus_section") == focus_section.get("key")
                ]
                if len(same_section_rounds) >= 3:
                    deltas = [
                        same_section_rounds[i + 1]["score"] - same_section_rounds[i]["score"]
                        for i in range(len(same_section_rounds) - 1)
                    ]
                    if all(abs(d) < 0.01 for d in deltas[-3:]):
                        # 该维度原地踏步，强制切换到最弱维度
                        _dim_scores = score_history[-1].get("dim_scores", {})
                        _weakest = min(_dim_scores, key=_dim_scores.get) if _dim_scores else None
                        if _weakest and _weakest != focus_section.get("key"):
                            for _sec in PROPOSAL_SECTIONS:
                                if _sec.get("key") == _weakest:
                                    focus_section = _sec
                                    break
                            if _log:
                                _log.info(
                                    f"[{proposal_id}] 维度轮换: {section_cycle}→{focus_section['key']}"
                                    f"（连续3轮原地踏步，切换到最弱维度）"
                                )
        else:
            focus_section = None  # 第4轮做整体一致性审查
            is_full_review = True

        # 读取当前申请书
        proposal_path = prop_dir / "04_proposal" / "proposal-draft.md"
        if not proposal_path.exists():
            return {"success": False, "error": "申请书不存在，请先执行管线生成初稿"}

        score_before = prop_state.get("last_score", 0.0)

        # v6.8.17: 加载历史人工审核反馈（反馈闭环——从对话中学习）
        # _run_critic 内部会各自加载 _load_human_feedback_block（v6.8.19 修复：
        # 避免跨方法 NameError），optimize_cycle 层不再重复加载

        # 1. critic 评审
        if _log:
            section_name = focus_section["cn"] if focus_section else "整体一致性"
            _log.info(f"[{proposal_id}] 对抗轮 {current_round + 1}: critic 评审（聚焦：{section_name}）")
        # v6.8.7: 程序化 AI 写作模式检测——在 critic 之前运行，产出表达质量天花板
        sections_obj = ProposalSections(prop_dir / "04_proposal")
        sections_obj.ensure_split()
        # v6.8.38: 基于实际 sections 文件重算 missing_sections。该字段只在初始化时写入
        # (initialization.py)，之后 writer 补全模块也不刷新，会停留在旧值（如 moire 曾标
        # 缺 innovation/plan/outcome，但这些压根不在 5 标准模块内、且文件实际都在），导致
        # critic 被引导去"重点检查"已存在的模块。此处每轮按 section_exists(内容>50字)重算
        # 并回写 prop_state，让 critic 聚焦真正缺失/空置的模块。
        missing_sections = [s["key"] for s in PROPOSAL_SECTIONS
                            if not sections_obj.section_exists(s["key"])]
        if missing_sections != prop_state.get("missing_sections"):
            prop_state["missing_sections"] = missing_sections
            self._set_proposal_state(proposal_id, prop_state)
        ai_check = self._detect_ai_patterns(prop_dir, sections_obj)
        if _log:
            _log.info(f"[{proposal_id}] AI 检测: ceiling={ai_check['ceiling']:.2f}, "
                       f"issues={len(ai_check['top_issues'])}")

        critic_result = self._run_critic(
            proposal_id, prop_dir, project_type, current_round + 1, critic_timeout,
            focus_section=focus_section, is_full_review=is_full_review,  # P1-1
            missing_sections=missing_sections,
            ai_check_result=ai_check,  # v6.8.7: 传入程序化检测结果
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
        pre_dims = self._extract_dimension_scores(critic_result, min_output_len=300)
        pre_weakest = self._get_weakest_dimension(pre_dims)

        # P1-2: 文献定向补充（严谨性不足时触发 researcher 检索）
        lit_supplement = ""
        if pre_dims.get("rigor", 1.0) < 0.70 or self._has_lit_gap(critic_result):
            if _log:
                _log.info(f"[{proposal_id}] 对抗轮 {current_round + 1}: researcher 定向检索文献缺口")
            lit_supplement = self._run_researcher_targeted(
                proposal_id, prop_dir, critic_result, focus_section,
                timeout=600,
            )

        # 2. writer 根据评审意见优化
        if _log:
            _log.info(f"[{proposal_id}] 对抗轮 {current_round + 1}: writer 优化")
        writer_result = self._run_writer_optimize(
            proposal_id, prop_dir, project_type, critic_result, writer_timeout,
            weakest_dim=pre_weakest, dim_scores=pre_dims,  # P0-2
            focus_section=focus_section, is_full_review=is_full_review,  # P1-1
            lit_supplement=lit_supplement,  # P1-2
            missing_sections=missing_sections,
            ai_check_result=ai_check,  # v6.8.7: 传入程序化检测结果
            round_num=current_round + 1,  # v6.10.26: 报告读盘按 section 分流
        )
        if _log:
            elapsed = writer_result.get("elapsed_s", 0)
            _log.info(
                f"[{proposal_id}] 对抗轮 {current_round + 1}: writer 完成 "
                f"success={writer_result.get('success')} elapsed={elapsed}s"
            )

        # 3. 解析新分数（v6.6.3：优先从 critic 写入的 report_path 文件读取，
        #    hermes stdout 摘要通常只截取前几行，遗漏末尾的"## 评分"代码块）
        # v6.10.26: 读盘与 _run_critic 写盘同口径（section 感知）
        report_path = _critic_report_path(
            prop_dir, current_round + 1,
            focus_section.get("key") if focus_section else "full_review",
        )

        # v6.7.1: critic 通过 hermes agent loop 异步写盘，等待文件生成且稳定
        if not (report_path.exists() and report_path.stat().st_size > 100):
            waited = self._wait_for_critic_report(report_path, timeout=30)
            if waited and _log:
                _log.info(f"[{proposal_id}] critic 报告已生成: {report_path.name}")

        critic_text = ""
        if report_path.exists() and report_path.stat().st_size > 100:
            try:
                file_content = report_path.read_text(encoding="utf-8")
                critic_text = file_content
                file_result = {"output": file_content}
                score_after = self._extract_score(file_result)
                dim_scores = self._extract_dimension_scores(file_result, min_output_len=300)  # P0-2
                issues = self._extract_issues(file_result)
            except Exception as e:
                if _log:
                    _log.warning(f"[{proposal_id}] 读取 critic 报告失败: {e}，回退到 stdout")
                # 回退：使用 hermes stdout 摘要
                critic_text = (critic_result or {}).get("output", "")
                score_after = self._extract_score(critic_result)
                dim_scores = self._extract_dimension_scores(critic_result, min_output_len=300)
                issues = self._extract_issues(critic_result)
        else:
            # 文件未生成（critic 未写盘），用 stdout 摘要
            if _log:
                _log.warning(f"[{proposal_id}] critic 报告未生成，使用 stdout 摘要评分")
            critic_text = (critic_result or {}).get("output", "")
            score_after = self._extract_score(critic_result)
            dim_scores = self._extract_dimension_scores(critic_result, min_output_len=300)
            issues = self._extract_issues(critic_result)
        weakest_dim = self._get_weakest_dimension(dim_scores)

        # v7.2.61: cap 前原始分留痕——四层天花板（表达 ceiling / references
        # 2 维重算 / 综合分 cap / 锚点绑定）把分数压进 0.74-0.85 窄带，但
        # score_history 此前只记 cap 后值，原始分只存在于 critic 报告文件。
        # 补记 score_raw + cap_applied，使验收判据与审计无需重读报告即可
        # 还原真值（瓶颈诊断 2026-10-30 P0 建议 3）。
        score_raw = round(float(score_after), 4)
        cap_applied = []

        # v6.8.7: 程序化天花板强制执行——表达质量得分不得超过 AI 检测产出的天花板
        if ai_check and "expression" in dim_scores:
            ceiling = ai_check.get("ceiling", 1.0)
            if dim_scores["expression"] > ceiling:
                if _log:
                    _log.warning(
                        f"[{proposal_id}] 表达质量 {dim_scores['expression']:.2f} > 天花板 {ceiling:.2f}，"
                        f"强制 cap 至 {ceiling:.2f}"
                    )
                dim_scores["expression"] = ceiling
                cap_applied.append("expression_ceiling")
                # 重新计算综合分
                score_after = self._recalculate_score(dim_scores, project_type)

        # v6.8.8: references 评审专用计分——N/A 维度不纳入加权
        section_key_for_check = focus_section["key"] if focus_section else "full_review"
        if section_key_for_check == "references" and dim_scores:
            # references 评审：综合分 = (严谨性 + 完整性) / 2，忽略 N/A 维度
            ref_dims = {k: v for k, v in dim_scores.items() if k in ("rigor", "completeness") and v > 0}
            if ref_dims:
                score_after = sum(ref_dims.values()) / len(ref_dims)
                cap_applied.append("references_2d_recalc")
                if _log:
                    _log.info(f"[{proposal_id}] references 评审专用计分: {score_after:.2f} (dims={ref_dims})")

        # v6.8.8: 综合分天花板——scoring_integrity_rules.rule_1
        # AI 检测天花板低时，综合分也必须受限，防止其他维度高分掩盖表达质量短板
        # v7.2.39（BUG-6）：本段必须排在 references 专用计分「之后」。此前两者
        # 顺序颠倒，references 轮的 ref 重算直接覆写 cap 结果，天花板对
        # references 轮 100% 失效——全库 42 个 references 轮中 5 轮逃逸
        # （ssh-weyl 0.95 / attosecond 0.91 / moire 0.90 / bsv 0.89 /
        # key-transient 0.84，均超各自 overall_ceiling）。
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
                cap_applied.append(f"overall_ceiling:{overall_ceiling:.2f}")

        # v6.9.25: 锚点对比结论与评分档位强制绑定——范本锚点成为分数锚
        # v6.9.28: ①移至 references 专用计分之后（原顺序在前者的赋值下被覆盖，
        #          references 轮绑定形同虚设）；②references 评审跳过绑定——其口径为
        #          rigor/completeness（文献元数据准确性），写作语体锚点不适用，
        #          "差距明显"（引用错位）不应 cap 元数据评审分
        anchor_conclusion = ""
        if section_key_for_check != "references":
            anchor_conclusion = self._extract_anchor_conclusion(critic_text)
            _pre_anchor_score = score_after
            score_after = self._apply_anchor_conclusion_binding(
                proposal_id, critic_text, dim_scores, score_after, project_type
            )
            if score_after != _pre_anchor_score:
                cap_applied.append("anchor_binding")

        # v6.8.8: 评审报告完整性验证——anti_superficial_review.programmatic_validation
        report_invalid_reason = ""
        if report_path.exists() and report_path.stat().st_size > 100:
            try:
                report_content = report_path.read_text(encoding="utf-8")
                has_anchor = "锚点对比" in report_content or "范本对标" in report_content
                has_style = "写作风格" in report_content
                # references 评审不需要锚点对比和写作风格评估
                if section_key_for_check != "references":
                    if not has_anchor:
                        report_invalid_reason = "缺少'锚点对比'段落"
                    elif not has_style:
                        report_invalid_reason = "缺少'写作风格评估'段落"
                if report_invalid_reason and _log:
                    _log.warning(f"[{proposal_id}] 评审报告不完整: {report_invalid_reason}")
            except Exception:
                pass

        # P1-1: 确定本轮模块 key
        section_key = focus_section["key"] if focus_section else "full_review"

        # P1-3: 判断该模块是否"对抗胜利"（分数达标 + 各维度无短板）
        min_score = threshold.get("min_overall_score", DEFAULT_SCORE_THRESHOLD)
        weak_dims = [
            k for k, floor in self.DIMENSION_FLOOR.items()
            if k in dim_scores and dim_scores[k] < floor
        ]
        # v7.3.41: A 通道判定改用 cap 前原始四维加权分（score_raw），解除
        # overall_ceiling 对科学质量的文风一票否决；score_after 仍为 cap 后
        # 值，继续用于总评展示/看板/其它环节（不改阈值、权重与 rubric 档位）。
        _gate_cal = _a_gate_calibers(score_after, score_raw)
        # v6.8.8: 评审报告不完整（缺锚点对比/写作风格评估）时强制不通过
        section_passed = (
            _gate_cal["gate"] >= min_score
            and len(weak_dims) == 0
            and not report_invalid_reason
        )

        # 4. 更新状态
        # v6.7.1：_set_proposal_state 内部已加 file_lock("proposal-lifecycle")，
        # 不再外层包 file_lock(f"proposal-{proposal_id}")，避免嵌套锁和潜在竞态
        prop_state = self._get_proposal_state(proposal_id)
        prop_state["optimization_rounds"] = current_round + 1
        # v6.8.21: 清理旧轮次 job
        from lifecycle.utils import archive_old_round_jobs
        archive_old_round_jobs(proposal_id, current_round + 1)
        prop_state["last_score"] = score_after
        prop_state["last_dim_scores"] = dim_scores  # P0-2: 记录维度分数
        # P1-3: 记录各模块对抗胜利状态
        section_passes = prop_state.get("section_passes", {})
        section_passes[section_key] = section_passed
        prop_state["section_passes"] = section_passes
        prop_state["score_history"].append({
            "round": current_round + 1,
            "score": score_after,
            # v7.2.61: cap 前原始分与 cap 链留痕（审计与验收判据用）
            "score_raw": score_raw,
            "cap_applied": cap_applied,
            "dim_scores": dim_scores,  # P0-2
            "weakest_dim": weakest_dim,  # P0-2
            "focus_section": section_key,  # P1-1
            "section_passed": section_passed,  # P1-3
            # v7.3.41: A 通道判定口径留痕（display=cap 后分，gate=判定分）
            "gate_score": round(_gate_cal["gate"], 4),
            "gate_caliber": _gate_cal["caliber"],
            # v6.10.3 F1: 口径标记——references 为 2 维专用口径（rigor/
            # completeness），章节为 4 维加权口径。下游（看板/dossier/
            # 逃生阀警告）据此区分，防止异口径分被当整篇分读。
            "caliber": "references_2d" if section_key == "references" else "section_4d",
            "issues_count": len(issues),
            "high_issues": sum(1 for i in issues if i.get("severity") == "high"),
            # v6.9.25: 程序化 AI 检测摘要随轮次入史——prompt_optimizer 聚合
            # 全局 top_issues 生成针对性修复指令，闭合"检测扣分→优化器
            # 看不见"的断点（实测 08-18：三课题 ceiling 触底 0.5，而优化器
            # 9 条建议无一指向超长句/冗余词/自引用）。
            "ai_ceiling": round(ai_check.get("ceiling", 1.0), 3),
            "ai_top_issues": (ai_check.get("top_issues") or [])[:6],
            # v6.9.28: 锚点对比结论随轮次入史——范本引导效果可观测
            # （达标/基本接近/差距明显；references 轮为空串）
            "anchor_conclusion": anchor_conclusion,
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

        # v6.7.11: full_review 轮同步更新课题设想、方法学手册、文献阅读笔记
        if is_full_review and writer_result.get("success"):
            try:
                sync_result = self._sync_derivative_artifacts(proposal_id, prop_dir, timeout=300)
                if _log:
                    _log.info(
                        f"[{proposal_id}] 同步产物完成 success={sync_result.get('success')}"
                    )
            except Exception as e:
                if _log:
                    _log.warning(f"[{proposal_id}] 同步产物失败: {e}")

        # v6.8.33: 轮次完成后立即同步知识库（事件驱动），覆盖 cron sweep/CLI 所有调用方
        try:
            from lifecycle.micro_scheduler import _sync_proposal_to_kb
            _sync_proposal_to_kb(proposal_id)
        except Exception as e:
            if _log:
                _log.warning(f"[{proposal_id}] 轮次完成 KB 同步失败: {e}")

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

    # v6.9.47: 领域术语白名单——这些复合词是科研写作/国基金模板的法定用法，
    # 裸词计数会误伤（实测 attosecond 课题：'关键科学问题'×5 是 NSFC 模板章节、
    # '系统误差'是物理术语、'有效性'=validity、'同时电离'=simultaneous ionization，
    # 全部不可删——导致 writer 修复指令物理上不可执行，天花板卡死 0.50）。
    # 计数前先替换为占位符，只统计真正的冗余用法。
    AI_TERM_WHITELIST = [
        "关键科学问题",      # NSFC 法定章节名
        "关键难点",          # NSFC 模板常见章节
        "系统误差",          # systematic error，物理术语
        "系统偏差",          # systematic bias
        "系统性",            # systematic(ally)，如"系统性研究/系统性成果"
        "有效性",            # validity，如"修正项有效性"
        "同时电离",          # simultaneous ionization，物理概念
        "同时或近同时电离",  # "一个以上电子被同时或近同时电离"
        "同时性",            # simultaneity
    ]

    def _detect_ai_patterns(
        self,
        prop_dir: Path,
        sections: 'ProposalSections',
        section_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """程序化检测申请书中的 AI 写作模式，产出表达质量天花板。

        这是评审跑偏的核心修复：不再让 LLM 凭感觉判断 AI 味，
        而是用代码客观计数，产出 expression_quality_ceiling，
        critic 的表达质量评分不得超过此天花板。

        v6.9.47 三项公平性修复：
            ① 领域术语白名单（AI_TERM_WHITELIST）——计数前剔除法定复合词，
              防止"关键科学问题/系统误差/有效性/同时电离"等不可删词被误伤；
            ② 阈值千字归一——死板关联词/冗余修饰词阈值随篇幅线性放宽
              （绝对阈值只对小篇幅合理，14K 字长文按 12 次上限意味着
              0.86 次/千字，中文科研写作正常密度 2-4 次/千字，物理不可达）；
            ③ raw_ceiling 字段——floor(0.5) 之前的原始值，供复检比较
              真实进步（floor 会把 0.6→0.5 的实质改善掩埋成 0.50→0.50）；
            ④ section_key 参数——章节级检测（单章节文本+按该章节字数
              归一阈值），供章节级 job 复检归因，避免 writer 只修聚焦
              章节但被三章节合并口径稀释。

        Args:
            prop_dir: proposal 目录
            sections: ProposalSections 实例
            section_key: 传入 "rationale"/"content"/"scheme" 时只检测该章节
                         （None 检测三章节合并，口径与 critic 全局评分对齐）

        Returns:
            {
                "ceiling": float,              # 表达质量天花板 (0.5-1.0)
                "raw_ceiling": float,          # floor 前原始值（复检比较用）
                "total_chars": int,            # 全文字符数
                "details": {                   # 各检测项详情
                    "transition_words": {"count": N, "threshold": N, "penalty": float},
                    "template_phrases": {...},
                    "template_subject": {...},
                    "redundant_modifiers": {...},
                    "long_sentences": {...},
                    "meta_discourse": {...},
                    "excessive_bold": {...},
                    "bullet_list_substitution": {...},
                },
                "report_text": str,            # 供 critic/writer prompt 使用的文本报告
                "top_issues": List[str],       # 最严重的 AI 模式问题（供 writer 优先修复）
            }
        """
        import re

        # 读取正文章节内容（section_key 指定时只读该章节——章节级归因口径）
        body_keys = [section_key] if section_key in ("rationale", "content", "scheme") \
            else ["rationale", "content", "scheme"]
        texts = []
        for key in body_keys:
            try:
                txt = sections.read_section(key)
                # v6.9.59: 剥离内嵌参考文献表——kt/qg 等课题的文献表内嵌在
                # 章节文件尾部（### 参考文献），文献条目是"引用数据"而非
                # "写作表达"，计入检测会把长条目误判为超长句（实测 kt 一篇
                # 72 条文献表贡献 11 处假超长句，天花板被错误压至 0.50）
                cut = txt.find("### 参考文献")
                if cut > 0:
                    txt = txt[:cut]
                if txt.strip():
                    texts.append(txt)
            except Exception:
                pass

        if not texts:
            return {"ceiling": 0.5, "raw_ceiling": 0.5, "total_chars": 0, "details": {},
                    "report_text": "（无法读取申请书内容）", "top_issues": []}

        full_text = "\n\n".join(texts)
        total_chars = len(full_text)
        if total_chars == 0:
            return {"ceiling": 0.5, "raw_ceiling": 0.5, "total_chars": 0, "details": {},
                    "report_text": "（申请书内容为空）", "top_issues": []}

        ceiling = 1.0
        details: Dict[str, Any] = {}
        top_issues: List[str] = []

        # v6.9.47: 领域术语白名单——替换为等长占位符后再计数，
        # 只统计真正的冗余用法（法定复合词不计入）
        text_for_count = full_text
        # v6.9.50: 长词优先替换——"同时或近同时电离"(8字)必须先于"同时电离"
        # (4字)遮蔽，否则长词尾部被短词占位后，残余"同时或近"中的"同时"
        # 泄漏计数 1 次（08-24 健康检查实证）。按长度降序对白名单未来
        # 新增重叠词条同样稳健。
        for term in sorted(self.AI_TERM_WHITELIST, key=len, reverse=True):
            text_for_count = text_for_count.replace(term, "□" * len(term))

        # 1. 死板关联词
        ai_transitions = ["在此基础上", "此外", "同时", "与此同时", "因此", "然而", "基于此"]
        transition_count = sum(text_for_count.count(w) for w in ai_transitions)
        # v6.9.47: 阈值千字归一——绝对阈值 8 只对小篇幅合理；
        # 中文科研写作正常关联词密度约 1 次/千字，按 1.0/千字放宽
        transition_threshold = max(8, int(total_chars / 1000 * 1.0))
        transition_penalty = max(0, (transition_count - transition_threshold) * 0.02)
        ceiling -= transition_penalty
        details["transition_words"] = {
            "count": transition_count, "threshold": transition_threshold,
            "penalty": round(transition_penalty, 4),
            "found": {w: text_for_count.count(w) for w in ai_transitions if text_for_count.count(w) > 0}
        }
        if transition_penalty > 0:
            top_issues.append(f"死板关联词超标：{transition_count}次（阈值{transition_threshold}），扣{transition_penalty:.2f}")

        # 2. 模板句式 "为...提供...基础/支撑/途径"
        template_patterns = [
            r"为.{1,20}提供.{0,10}(基础|支撑|途径|条件|工具|指导)",
        ]
        template_count = sum(len(re.findall(p, full_text)) for p in template_patterns)
        template_threshold = 8
        template_penalty = max(0, (template_count - template_threshold) * 0.03)
        ceiling -= template_penalty
        details["template_phrases"] = {
            "count": template_count, "threshold": template_threshold,
            "penalty": round(template_penalty, 4)
        }
        if template_penalty > 0:
            top_issues.append(f"模板句式'为...提供...'超标：{template_count}次（阈值{template_threshold}），扣{template_penalty:.2f}")

        # 3. 模板主语 "本项目拟/本项目将" 句首
        # 按句号分句，检查句首
        sentences = re.split(r'[。！？\n]', full_text)
        subject_patterns = ["本项目拟", "本项目将", "本项目计划", "本项目旨在"]
        subject_count = sum(1 for s in sentences if any(s.strip().startswith(p) for p in subject_patterns))
        subject_threshold = 5
        subject_penalty = max(0, (subject_count - subject_threshold) * 0.02)
        ceiling -= subject_penalty
        details["template_subject"] = {
            "count": subject_count, "threshold": subject_threshold,
            "penalty": round(subject_penalty, 4)
        }
        if subject_penalty > 0:
            top_issues.append(f"模板主语'本项目拟/将'句首超标：{subject_count}次（阈值{subject_threshold}），扣{subject_penalty:.2f}")

        # 4. 冗余修饰词（v6.9.47: 白名单过滤 + 千字归一）
        redundant_words = ["显著", "重要", "系统", "良好", "成熟", "完整", "关键", "精准", "一系列", "有效", "高效"]
        redundant_count = sum(text_for_count.count(w) for w in redundant_words)
        # v6.9.47: 阈值千字归一——绝对阈值 12 对 14K 字长文意味着 0.86 次/千字，
        # 中文科研写作正常密度 2-4 次/千字，按 2.0/千字放宽
        redundant_threshold = max(12, int(total_chars / 1000 * 2.0))
        redundant_penalty = max(0, (redundant_count - redundant_threshold) * 0.01)
        ceiling -= redundant_penalty
        details["redundant_modifiers"] = {
            "count": redundant_count, "threshold": redundant_threshold,
            "penalty": round(redundant_penalty, 4),
            "found": {w: text_for_count.count(w) for w in redundant_words if text_for_count.count(w) > 0}
        }
        if redundant_penalty > 0:
            top_issues.append(f"冗余修饰词超标：{redundant_count}次（阈值{redundant_threshold}），扣{redundant_penalty:.2f}")

        # 5. 超长句（v6.9.47: 免赔额——长文自然含更多长句，前 2+0.15/千字 处免赔）
        severe_count = sum(1 for s in sentences if len(s.strip()) > 120)
        long_free = 2 + int(total_chars / 1000 * 0.15)
        long_penalty = max(0, severe_count - long_free) * 0.02
        ceiling -= long_penalty
        details["long_sentences"] = {
            "severe_count": severe_count, "free_quota": long_free,
            "penalty": round(long_penalty, 4),
            "examples": [s.strip()[:80] + "..." for s in sentences if len(s.strip()) > 120][:3]
        }
        if long_penalty > 0:
            top_issues.append(f"超长句(>120字)：{severe_count}处（免赔{long_free}处），扣{long_penalty:.2f}")

        # 6. 元话语
        meta_patterns = [
            r"沿着.{0,10}这一主线", r"我们可以辨识", r"构成本项目的.{0,6}基线",
            r"一个根本性问题.{0,6}浮现", r"需要特别说明的是", r"需要澄清的是",
            r"需要指出的是", r"值得注意的是", r"这一判断构成", r"这一跃迁携带",
        ]
        meta_count = sum(len(re.findall(p, full_text)) for p in meta_patterns)
        meta_threshold = 2
        meta_penalty = max(0, (meta_count - meta_threshold) * 0.03)
        ceiling -= meta_penalty
        details["meta_discourse"] = {
            "count": meta_count, "threshold": meta_threshold,
            "penalty": round(meta_penalty, 4)
        }
        if meta_penalty > 0:
            top_issues.append(f"元话语超标：{meta_count}次（阈值{meta_threshold}），扣{meta_penalty:.2f}")

        # 7. 过度加粗
        bold_count = len(re.findall(r'\*\*[^*]+\*\*', full_text))
        bold_per_1k = bold_count / max(total_chars, 1) * 1000
        bold_threshold = 3  # per 1k chars
        bold_excess = max(0, bold_per_1k - bold_threshold)
        bold_penalty = 0.0
        if bold_excess > 0:
            bold_penalty = min(0.15, int(bold_excess) * 0.03)  # 最多扣0.15
        ceiling -= bold_penalty
        details["excessive_bold"] = {
            "count": bold_count, "per_1k_chars": round(bold_per_1k, 2),
            "threshold_per_1k": bold_threshold, "penalty": round(bold_penalty, 4)
        }
        if bold_penalty > 0:
            top_issues.append(f"加粗标记过多：{bold_count}处（{bold_per_1k:.1f}/千字，阈值{bold_threshold}/千字），扣{bold_penalty:.2f}")

        # 8. 编号列表替代论述
        # 检测连续的 "1. xxx\n2. xxx" 或 "- xxx\n- xxx" 模式
        list_blocks = len(re.findall(r'(?:^|\n)(?:\d+\.\s+.+(?:\n|$)){2,}', full_text))
        list_blocks += len(re.findall(r'(?:^|\n)(?:[-*]\s+.+(?:\n|$)){2,}', full_text))
        list_penalty = min(0.20, list_blocks * 0.05)
        ceiling -= list_penalty
        details["bullet_list_substitution"] = {
            "count": list_blocks, "penalty": round(list_penalty, 4)
        }
        if list_penalty > 0:
            top_issues.append(f"编号/bullet列表替代论述：{list_blocks}处，扣{list_penalty:.2f}")

        # 9. 自引用泛滥（v6.8.8: scoring_integrity_rules.rule_7）
        self_ref_patterns = [
            r"详\s*§\d", r"见\s*§\d", r"方法学手册\s*§\d",
            r"与\s*§\d\s*一致", r"详见\s*§\d", r"参见\s*§\d",
            r"详\s*§\d\.\d", r"见\s*§\d\.\d", r"方法学手册\s*§\d\.\d",
        ]
        self_ref_count = sum(len(re.findall(p, full_text)) for p in self_ref_patterns)
        self_ref_penalty = 0.0
        if self_ref_count > 15:
            self_ref_penalty = 0.10
        elif self_ref_count > 10:
            self_ref_penalty = 0.05
        ceiling -= self_ref_penalty
        details["self_reference"] = {
            "count": self_ref_count, "threshold_1": 10, "threshold_2": 15,
            "penalty": round(self_ref_penalty, 4)
        }
        if self_ref_penalty > 0:
            top_issues.append(f"自引用泛滥：{self_ref_count}次（阈值10/15），扣{self_ref_penalty:.2f}")

        # 天花板下限（v6.9.47: 保留 floor 前原始值供复检比较——
        # floor 会把 0.6→0.5 的实质改善掩埋成 0.50→0.50，writer 被误判）
        raw_ceiling = ceiling
        ceiling = max(ceiling, 0.5)

        # 构建报告文本
        report_lines = [
            f"【程序化 AI 写作模式检测报告】",
            f"全文字符数：{total_chars}",
            f"表达质量天花板：{ceiling:.2f}（critic 表达质量评分不得超过此值）",
            f"",
            f"各检测项详情：",
        ]
        for name, info in details.items():
            if info.get("penalty", 0) > 0:
                report_lines.append(f"  ⚠️ {name}: {info}")
            else:
                report_lines.append(f"  ✓ {name}: {info}")

        if top_issues:
            report_lines.append(f"")
            report_lines.append(f"最严重的 AI 模式问题（writer 必须优先修复）：")
            for issue in top_issues:
                report_lines.append(f"  - {issue}")

        report_text = "\n".join(report_lines)

        if _log:
            _log.info(f"AI pattern detection: ceiling={ceiling:.2f} (raw={raw_ceiling:.2f}), "
                       f"total_chars={total_chars}, issues={len(top_issues)}"
                       + (f", section={section_key}" if section_key else ""))

        return {
            "ceiling": round(ceiling, 4),
            "raw_ceiling": round(raw_ceiling, 4),
            "total_chars": total_chars,
            "section_key": section_key,
            "details": details,
            "report_text": report_text,
            "top_issues": top_issues,
        }

    def _build_enforcement_checklist_text(
        self,
        standards_path: str,
        focus_section: Optional[Dict[str, str]],
        is_full_review: bool,
    ) -> str:
        """v6.8.8: 从 nsfc-standards.json 读取 enforcement_checklist 并格式化为 prompt 文本。

        这是评审跑偏的核心修复：不再依赖 LLM 读取 JSON 文件中的 review_checklist，
        而是由程序读取并直接嵌入 prompt，确保 LLM 能看到具体的检查条目。
        """
        try:
            standards = load_json(Path(standards_path), default={})
        except Exception:
            return ""

        section_standards = standards.get("section_standards", {})

        # 确定要读取的 section key
        if is_full_review:
            section_key = "full_review"
        elif focus_section:
            section_key = focus_section.get("key", "")
        else:
            section_key = ""

        if not section_key:
            return ""

        section_def = section_standards.get(section_key, {})
        ec = section_def.get("enforcement_checklist", {})
        items = ec.get("items", [])
        if not items:
            return ""

        # 格式化为 prompt 文本
        lines = [
            f"\n【执行清单（{section_def.get('cn', section_key)}——必须逐条检查，每条给出'通过/不通过'判断）】",
        ]
        for item in items:
            lines.append(f"  {item['id']}. {item['check']}")
            lines.append(f"     通过条件：{item['pass_if']}")
        lines.append("")
        lines.append("不通过条目数 > 3 时，该 section 得分不得高于 0.70。")
        lines.append("评审报告中必须包含'执行清单对照'段落，逐条报告通过/不通过状态。")
        lines.append("")

        # 添加锚点对比要求
        mc = section_def.get("mandatory_comparison", {})
        if mc:
            lines.append(f"【锚点对比（{section_def.get('cn', section_key)}——评审报告中必须包含，缺失则评审无效）】")
            lines.append(f"  格式：{mc.get('format', '引用申请书原文→引用锚点→指出差距→给出档位判定')}")
            for pair in mc.get("anchor_pairs", []):
                lines.append(f"  对比对：{pair}")
            lines.append(f"  {mc.get('blocking_rule', '缺失则评审无效')}")
            lines.append("")

        return "\n".join(lines)

    def _run_critic(
        self,
        proposal_id: str,
        prop_dir: Path,
        project_type: str,
        round_num: int,
        timeout: int,
        focus_section: Optional[Dict[str, str]] = None,
        is_full_review: bool = False,
        missing_sections: Optional[List[str]] = None,
        ai_check_result: Optional[Dict[str, Any]] = None,
        params_check_text: str = "",  # v7.2.13: 口径校验结论注入（含冲突清单）
    ) -> Dict[str, Any]:
        """派活给 critic profile 做对抗评审。

        P1-1: 支持章节级评审（focus_section）和整体审查（is_full_review）。
        v6.7.7: 默认按章节拆分文件读取，降低单次 LLM 负载、减少超时。
        v6.8.3-fix10: references 模块使用轻量化专用 prompt，不走重型评审流程。
        """
        sections = ProposalSections(prop_dir / "04_proposal")
        sections.ensure_split()  # 兼容旧格式：自动拆分
        standards_path = str(self.standards_path.relative_to(_pl.PROJECT_ROOT))
        # v6.10.26: section 感知写盘——同轮多 section 分文件，杜绝互覆
        # （旧约定共用裸名 critic-round-{n}.md，章节轮被后写的 references
        # 报告覆盖，读盘得到 2 维伪分，见 _critic_report_path docstring）
        _sec_key = focus_section.get("key") if focus_section else "full_review"
        report_path = _critic_report_path(prop_dir, round_num, _sec_key)
        report_path.parent.mkdir(parents=True, exist_ok=True)

        # v6.7.7: 构建要读取的文件列表
        is_references = focus_section and focus_section.get("key") == "references"

        if is_references:
            # v6.9.42: references 评审任务重排——程序化预检 + 输入瘦身。
            # 旧安排的三处结构性缺陷（08-24 诊断，bsv/order-param 连续超时根因）：
            # ① 输入超载：critic 被要求读 references.md（40KB，其中 60% 是
            #    writer 每轮追加的核校工作日志 §D-F）+ 三个正文章节（62KB）
            #    ≈ 106KB，900-1200s 跑不完；
            # ② 程序化任务交给 LLM："编号一致性"（正文 [N] ↔ 列表编号比对）
            #    本可正则完成，却让 critic 通读全文去找——而 references.md
            #    的 §D 映射表往往已经存在（writer 上轮核校的产物）；
            # ③ 核校日志污染文献文件：§E 核实声明/§F 闭环证据属 05_review
            #    域内容，写入 references.md 使其从 8KB 膨胀到 40KB。
            # 修复：预检程序化产出引用映射表（几 KB）附入 prompt，critic
            # 只读 references.md + 映射表，不再读正文章节——输入降至
            # ~45KB，LLM 聚焦其擅长的格式规范/时效性/相关性判断。
            ref_file = prop_dir / "04_proposal" / "sections" / "references.md"
            preflight = _references_preflight(prop_dir)
            prompt = (
                f"请对以下 NSFC 申请书的参考文献做第 {round_num} 轮检验。\n\n"
                f"【项目类型】{project_type}\n\n"
                f"【参考文献文件】{ref_file}\n\n"
                f"【程序化预检结果（编号一致性已由程序完成，请直接采信并引用）】\n"
                f"{preflight}\n\n"
                f"请执行以下检查（不需要检查写作风格、创新性或可行性；\n"
                f"编号一致性已由预检完成，不要重复逐条核对）：\n"
                f"1. 引文格式：作者、年份、期刊、卷页是否完整统一（DOI/arXiv 二选一）\n"
                f"2. 引用相关性：每条参考文献是否与申请书的科学问题相关，是否有无关引用\n"
                f"3. 缺失引用：结合预检的未引用条目与正文论断（凭预检信息判断，无需读正文全文）\n"
                f"4. 引用数量与时效性：总数是否在 20-40 篇区间，是否包含近 3 年文献\n\n"
                f"每个问题按严重程度分级（critical/high/medium/low），给出具体修改建议。\n"
                f"【输出契约（v6.9.86）】报告全文 ≤2500 字：问题清单每条一行"
                f"（`[severity]｜位置｜问题≤40字｜建议≤40字`），不做展开论证。\n"
                f"若预检已标记膨胀告警，请将'工作日志污染'列为问题并建议迁移至 05_review。\n\n"
                f"【评分（必填）】\n"
                f"只评两个维度（0-1），创新性和可行性标记为 N/A：\n"
                f"  - 严谨性（rigor）：引文格式、作者信息完整性\n"
                f"  - 完整性（completeness）：引用数量、时效性、缺失引用情况\n\n"
                f"在检验报告末尾，必须包含如下格式的评分块（供程序解析）：\n"
                f"```\n"
                f"## 评分\n"
                f"创新性：N/A\n"
                f"可行性：N/A\n"
                f"严谨性：0.75\n"
                f"完整性：0.90\n"
                f"综合评分：0.82\n"
                f"```\n"
                f"（注：创新性和可行性填 N/A，综合评分为严谨性和完整性的均值。\n"
                f"评分块必须是纯文本行——数字不要 **加粗**、不要放入 Markdown 表格，\n"
                f"否则程序解析会误读为权重列数值，历史实测 0.78 被记成 0.5）\n"
                f"将检验报告写入：{report_path}\n"
            )
            # v6.9.42: 输入从 106KB 降至 ~45KB 后曾回归 900s 基准；v6.9.82
            # 实测推翻（成功案例 840-1140s，900s 随机砍掉本可完成的 job），
            # 上限对齐 critic_writer_timeout_s 的 LARGE 档 1500s。
            return self._run_hermes("critic", prompt, min(timeout, 1500))

        elif is_full_review:
            focus_text = (
                f"\n【本轮为整体一致性审查】\n"
                f"请检查三个章节之间的逻辑衔接、术语一致性、内容冗余/矛盾。\n"
                f"不需要逐段细审，聚焦整体连贯性。\n\n"
            )
            # v6.9.46: full_review 输入瘦身 + 指标一致性程序化预检。
            # 旧安排读全部 5 章节（实测最大 ~180KB：48+46+47+33+39KB）+
            # standards 36KB，是超时大户（4 次）。两处同构修复：
            # ① references.md（39KB 纯文献列表）与"逻辑衔接/术语一致性/
            #    冗余矛盾"审查无关，排除——输入立减 ~40KB；
            # ② "指标红线：同一指标跨章节一致"的数字比对程序化完成，
            #    预检表附入 prompt，critic 直接采信。
            # v6.9.53: ③ full_review.md 自身也排除——它是"全文逻辑骨架"
            # （派生索引，非申请书内容），其纯净性由程序化预检把关，
            # 不需要 critic 通读（08-27 实证曾膨胀到 33KB 核查记录）。
            files_to_read = [
                str(prop_dir / "04_proposal" / "sections" / f"{s['key']}.md")
                for s in PROPOSAL_SECTIONS
                if sections.section_exists(s['key'])
                and s['key'] not in ("references", "full_review")
            ]
            metrics_preflight = _cross_section_metrics_preflight(prop_dir)
            # v6.9.53: 章节字数预算 + full_review 纯净性预检（零 LLM）
            # v6.9.55: 附冗余/无关程序检测线索——critic 深挖语义层冗余
            budget_preflight = budget_report_text(
                prop_dir / "04_proposal" / "sections")
            purity_preflight = full_review_purity_text(prop_dir)
            quality_preflight = quality_directives_text(prop_dir)
            read_instruction = (
                "【申请书章节文件】\n" +
                "\n".join(f"- {p}" for p in files_to_read) +
                "\n\n请读取以上章节文件，做整体一致性审查。\n"
                "（references.md 已排除——文献列表与逻辑衔接审查无关，\n"
                "其编号一致性由 references 专轮的程序化预检覆盖。\n"
                "full_review.md 已排除——它是程序维护的逻辑骨架索引，\n"
                "非申请书内容，其纯净性由下方预检把关。）\n\n"
                f"【跨章节指标一致性预检（程序完成，请直接采信）】\n{metrics_preflight}\n"
                f"【跨章节冗余程序检测（程序初筛，请复核语义层并扩展）】\n"
                f"{quality_preflight if quality_preflight else '（程序未检出归一化重复句——请自行检查改写式复述）'}\n"
                f"{budget_preflight}"
                f"{purity_preflight}"
            )
        elif focus_section:
            focus_text = (
                f"\n【本轮聚焦章节】{focus_section['title']}（{focus_section['desc']}）\n"
                f"请重点深入评审该章节，其他章节只做简要一致性检查。\n"
                f"对该章节的评审应细致到段落级别。\n\n"
            )
            # v6.10.0（T3）：scheme 聚焦轮提示方法页存在（不注入全文，
            # 只给路径——critic 可按需比对申请书数值与方法页参数表）
            if focus_section.get("key") == "scheme":
                focus_text += _methods_critic_hint()
            section_file = prop_dir / "04_proposal" / "sections" / f"{focus_section['key']}.md"
            files_to_read = [str(section_file)]
            # v6.9.53: 聚焦章节字数预算——超限属结构性问题（writer 只追加
            # 不删减的增量累积），必须按 critical"压缩重写"处置，程序化
            # 口径让 critic 免于目测。
            focus_budget = budget_report_text(
                prop_dir / "04_proposal" / "sections",
                focus_key=focus_section["key"],
            )
            read_instruction = (
                f"【申请书聚焦章节文件】{section_file}\n"
                f"请主要读取以上聚焦章节文件；如需检查跨章节一致性，可简要读取其他章节。\n\n"
                f"{focus_budget}"
            )
        else:
            focus_text = ""
            files_to_read = [str(prop_dir / "04_proposal" / "proposal-draft.md")]
            read_instruction = f"【申请书文件】{files_to_read[0]}\n"

        # v6.7.10: 模块完整性检查提示
        section_key_to_cn = {s["key"]: s["cn"] for s in PROPOSAL_SECTIONS}
        missing_cn = [section_key_to_cn.get(k, k) for k in (missing_sections or [])]
        completeness_hint = ""
        if missing_cn:
            completeness_hint = (
                f"\n【模块完整性警告】当前申请书缺失以下模块：{', '.join(missing_cn)}。\n"
                f"请在「严谨性」维度大幅扣分（缺 1 个模块不高于 0.5，缺 2 个及以上不高于 0.3），\n"
                f"并将每个缺失模块标记为 [critical] issue，要求 writer 必须补齐。\n"
            )

        # v7.0.0: 写作风格知识（叙述式违规/AI味/指标红线/内容越界/审计语言）
        # 已收敛至 .hermes/skills/nsfc-writing/SKILL.md，经
        # _load_nsfc_writing_skill_text('critic') 在 prompt 拼接处注入。
        # 此处只保留评分锚点回归契约（引用 JSON key 的编排指令）。
        narrative_rules = (
            "\n【评分锚点回归（强制要求）】\n"
            "- 评分时必须读取 general_principles.scoring_rubric，逐条对照档位描述打分\n"
            "- 评分时必须读取 reference_materials.benchmark_anchors，将申请书文字与范本锚点段落对比\n"
            "- 每条评审意见必须标注违反的 rubric 条款编号或标准条款名称\n"
            "- 若申请书存在 anti_ai_patterns 中列举的模式，表达质量直接扣至 0.6-0.7 区间\n"
            "- 若存在 indicator_red_lines 违规，严谨性直接扣至 0.6-0.7 区间\n"
            "- 不得凭感觉打分，必须给出档位依据\n"
            "问题按 P1（必改）/P2（强烈建议）/P3（建议）分级。\n"
        )

        # v6.8.7: 程序化 AI 检测结果（强制锚点回归机制）
        ai_check_text = ""
        if ai_check_result:
            ai_check_text = (
                f"\n{ai_check_result['report_text']}\n\n"
                f"⚠️ 强制约束：你的表达质量评分不得超过天花板 {ai_check_result['ceiling']:.2f}。\n"
                f"若天花板 < 0.7，你必须在评审报告中明示'程序化检测发现AI写作模式，表达质量被强制限制'。\n"
                f"你必须将检测到的 AI 模式问题列入问题清单，标注 issue_type='anti_ai'，severity ≥ [high]。\n"
            )

        # v6.8.8: 嵌入 section enforcement_checklist 到 prompt（不再依赖 LLM 读取 JSON）
        enforcement_checklist_text = self._build_enforcement_checklist_text(
            standards_path, focus_section, is_full_review
        )

        prompt = (
            f"请对以下 NSFC 申请书做第 {round_num} 轮对抗评审。\n\n"
            f"【项目类型】{project_type}\n"
            f"【质量标准】请读取 {standards_path}，重点关注：\n"
            f"  - section_standards（每个 section 的详细撰写要求和评审清单，必须逐条对照）\n"
            f"  - programmatic_checks（程序化检测规则和表达质量天花板）\n"
            f"  - overall_review_requirements（整体评审要求，含防跑偏规则）\n"
            f"  - project_types.{project_type} 的评审标准与权重\n"
            f"  - general_principles.writing_style_rules.anti_ai_patterns（去AI味量化阈值，文字规范见 prompt 内 skill 注入块）\n  - general_principles.scope_exclusion（范围排除：研究基础/工作条件/团队/经费不撰写不评审）\n"
            f"  - general_principles.indicator_red_lines（P0指标红线）\n"
            f"  - general_principles.scoring_rubric（评分档位标准，必须逐条对照打分）\n"
            f"  - reference_materials.style_benchmark（范本写作标杆摘要）\n"
            f"  - reference_materials.benchmark_anchors（范本锚点段落，评分时对比使用）\n\n"
            f"{read_instruction}"
            f"{focus_text}"
            f"{completeness_hint}"
            f"{ai_check_text}\n"
            f"{params_check_text}\n"
            f"{enforcement_checklist_text}\n"
            f"{narrative_rules}\n"
            f"{_load_nsfc_writing_skill_text('critic')}\n"
            f"请执行：\n"
            f"0. 模块完整性检查：确认申请书是否包含标准模块。\n"
            f"1. 读取指定的申请书文件和质量标准配置文件\n"
            f"2. 【强制】逐条对照'执行清单'，每条给出一行'通过/不通过'结论\n"
            f"3. 【强制】只选 2 个与聚焦章节最相关的 benchmark_anchors 锚点做对比"
            f"（引用申请书原文一句→引用锚点一句→差距一行），末尾给出结论行："
            f"`锚点对比结论：达标` 或 `锚点对比结论：基本接近` 或 `锚点对比结论：差距明显`\n"
            f"4. 【强制】引用程序化 AI 检测结果，将检测到的 AI 模式列入问题清单\n"
            f"5. 按项目类型标准做红队评审，尽可能找出问题\n"
            f"6. 重点检查写作风格：知识整理/文献罗列/条目式堆砌/缺乏连贯叙事，标记为 [high] narrative issue\n"
            f"7. 每个问题给出具体、可执行的修改建议，并标注违反的 rubric 条款或标准条款\n"
            f"8. 按严重程度分级（critical/high/medium/low）\n\n"
            # v6.9.86: 输出契约模板化收紧——软字数上限（6000字）实测无效
            # （报告仍 17-22KB），推理模型生成时间是 critic 超时的直接
            # 原因（09-01 实证：MiniMax 上也 1200s 触顶）。模板逐字段化
            # + 段落限量：下游解析（评分块/锚点结论行/issues 清单）完全
            # 兼容，展开论证只保留 P0/P1 各一段。
            f"【报告输出契约（硬性，超限的段落视为无效评审）】\n"
            f"报告全文 ≤4000 字，严格按以下模板逐段输出：\n"
            f"## 执行清单对照\n（每条一行：`清单N. 通过` 或 `清单N. 不通过——一句话依据`，不展开）\n"
            f"## 锚点对比\n（2 对锚点，每对三行：申请书原文一句 / 锚点原文一句 / 差距一行；"
            f"末尾一行 `锚点对比结论：…`）\n"
            f"## 写作风格评估\n（≤150 字结论 + 引用程序化检测结果行）\n"
            f"## 问题清单\n（≤8 条，每条一行：`[severity] issue_type｜位置｜问题（≤40字）｜修改建议（≤40字）`；"
            f"仅 critical 问题可追加一段 ≤100 字论证）\n"
            f"## 评分\n（按下方评分块格式，每维度附一行 rubric 档位依据）\n\n"
            f"【多维度评分（必填，按 scoring_rubric 档位打分）】\n"
            f"请从以下 4 个维度分别评分（0-1），每个维度必须引用 scoring_rubric 中对应档位描述作为依据：\n"
            f"  - 创新性（innovation）：科学问题是否新颖、方法是否有突破\n"
            f"  - 可行性（feasibility）：技术路线能否落地、是否有支撑\n"
            f"  - 严谨性（rigor）——五项核查清单逐项判定（v7.2.17 清单化，按过项数定档）：\n"
            f"     ①数值链一致（关键参数全篇单一口径，带单位与出处）\n"
            f"     ②指标定义可操作（判据给出计算式或测量协议，可第三方复算）\n"
            f"     ③文献支撑真实（抽查引用可溯源，无一虚构或张冠李戴）\n"
            f"     ④逻辑闭环（问题→假说→方法→验证每环有承接句，无跳跃）\n"
            f"     ⑤模块自洽（章节间无相互矛盾的表述/数值）\n"
            f"     定档：五项全过=0.90+（对标评审团亲审通过质量）/ 过四=0.80-0.89 /"
            f" 过三=0.70-0.79（必须指出未过的具体项与位置）/ 过二=0.60-0.69 / 过一以下<0.60。\n"
            f"     禁止印象式打分与 0.75 附近折中摇摆：降档必须指明未过项编号与位置。\n"
            f"  - 表达质量（expression）：是否连贯叙述式行文、是否消除AI味、是否对标范本水准\n"
            f"  ⚠️ 表达质量评分不得超过程序化天花板。若天花板 < 0.7，表达质量必须 ≤ 天花板。\n"
            f"  ⚠️ 锚点对比结论与评分档位强制绑定（v6.9.25，程序解析后强制执行）：\n"
            f"     - 结论=差距明显 → 表达质量 ≤ 0.69，综合评分 ≤ 0.84\n"
            f"     - 结论=基本接近 → 表达质量 ≤ 0.79，综合评分 ≤ 0.89\n"
            f"     - 结论=达标 → 表达质量方可进入 0.85+；综合评分要打 0.90+，必须在锚点对比中"
            f"对语体/论证密度/数据驱动/引用嵌入四项逐项举证不低于范本。\n"
            f"     你的自评分与锚点结论不一致时，以锚点结论对应的档位上限为准，先自行修正再提交。\n\n"
            f"在评审报告末尾，必须包含如下格式的评分块（供程序解析）：\n"
            f"```\n"
            f"## 评分\n"
            f"创新性：0.85\n"
            f"可行性：0.80\n"
            f"严谨性：0.75\n"
            f"表达质量：0.70\n"
            f"综合评分：0.78\n"
            f"```\n"
            f"将评审报告写入：{report_path}\n"
        )

        # v6.8.17: 注入历史人工审核反馈（反馈闭环）
        # v6.8.19 修复: 在 _run_critic 自己的作用域内加载，避免跨方法未定义 NameError
        _human_feedback_block = self._load_human_feedback_block(proposal_id)
        if _human_feedback_block:
            prompt += _human_feedback_block

        # v6.8.22: 注入历史遗留 P0 记忆（断裂点1）——critic 需核对这些历史问题是否仍存在
        _p0_memory = self._build_p0_memory_text(proposal_id, exclude_resolved=True)
        if _p0_memory:
            prompt += (
                _p0_memory
                + "请逐条核对这些历史遗留问题在当前申请书中是否仍存在：\n"
                + "  - 若仍存在，必须在问题清单中再次标记（severity 不变或更高），并引用具体段落\n"
                + "  - 若已解决，请明确说明'已解决'，避免误报\n"
                + "严禁因为历史问题曾出现就重复机械扣分，务必基于当前文本实际判断。\n"
            )

        # v6.8.18: 注入 agent 分数反馈——让 critic 看到自己的表现，才能调整
        _score_feedback = self._load_agent_score_feedback("critic")
        if _score_feedback:
            prompt += _score_feedback

        return self._run_hermes("critic", prompt, timeout)

    def _load_human_feedback_block(self, proposal_id: str) -> str:
        """v6.8.19: 加载历史人工审核反馈的 prompt 片段（仅当存在时返回非空字符串）。

        抽出该方法是因为原版在 optimize_cycle 局部变量中加载一次后，
        在 _run_critic 方法内被引用，导致跨方法作用域 NameError。
        通过 proposal_id 重新查询 prop_state，避免跨方法依赖。
        """
        prop_state = self._get_proposal_state(proposal_id) or {}
        try:
            from proposal_lifecycle.feedback_archive import load_review_feedback_for_optimization
            # v6.9.35: 显式传 proposal_id——prop_state 中无该键（见
            # feedback_archive.py docstring），旧实现恒返回空串闭环失效
            block = load_review_feedback_for_optimization(prop_state, proposal_id)
        except Exception:
            return ""
        return block or ""

    def _load_agent_score_feedback(self, role: str) -> str:
        """v6.8.18: 加载 agent 分数反馈——让 agent 看到自己的表现历史。

        只有当分数 <80（偏离初始 100 较远）或最近 3 轮有 reason 时才注入，
        避免无意义的冗余。

        v6.8.24: 修复 JSON 路径 bug——agent-scores.json 顶层直接是 role key，
        旧版读 scores["agents"][role] 永远返回空 dict，导致奖惩反馈完全失效。
        """
        try:
            import json
            from pathlib import Path
            scores_path = _pl.PROJECT_ROOT / "memory" / "agent-scores.json"
            if not scores_path.exists():
                return ""
            scores = json.loads(scores_path.read_text(encoding="utf-8"))
            # v6.8.24: 实际结构是 {role: {score, history, ...}}，不是 {agents: {role: ...}}
            agent = scores.get(role, {})
            score = agent.get("score", 100)
            initial = agent.get("initial_score", 100)
            history = agent.get("history", [])

            if score >= 80 and not history:
                return ""  # 分数健康，无需反馈

            lines = [
                f"\n\n【你的表现评价（累积分数 {score}/{initial}）】\n",
            ]

            # 最近 3 轮的反馈
            recent = history[-3:] if len(history) >= 3 else history
            if recent:
                lines.append("近期评价：\n")
                for h in recent:
                    delta = h.get("score", h.get("delta", 0))
                    reason = h.get("reason", "")
                    at = h.get("at", h.get("timestamp", ""))[:10]
                    if reason:
                        lines.append(f"- [{at}] 分数变化 {delta:+.1f}：{reason[:200]}\n")

            if score < 40:
                lines.append(
                    "\n⚠ 你的分数已严重偏低。请特别注意：\n"
                )
                if role == "critic":
                    lines.append(
                        "- 严格但准确：评分必须与申请书实际质量匹配，不要虚高也不要过度苛刻\n"
                        "- 每个问题都要有具体引用和可操作的改进建议\n"
                    )
                else:
                    lines.append(
                        "- 必须实质性回应当前 critic 的所有重要问题\n"
                        "- 避免表面修改（改了措辞但没改内容）\n"
                    )

            return "".join(lines) if len(lines) > 2 else ""
        except Exception:
            return ""

    # 表面修改评价关键词——monitor 的 writer_assessment 命中即视为"未实质修复"
    _SURFACE_KEYWORDS = (
        "未修复", "未解决", "未回应", "表面修改", "表面修复", "零改动",
        "未执行", "未实质", "修改有限", "修改极其有限", "未做", "搁置",
        "伪修复", "未处理",
    )

    def _build_writer_escalation_block(self, critic_report_path: str) -> str:
        """v6.9.28: writer 顽固升级——连续两轮被判定表面修改时强制逐条响应。

        背景：moire R2/R3 实测（08-20），writer 连续两轮被 monitor 判定
        表面修改/未修复（delta -16.9 / -8.5，修复率 1/7）。惩罚在累积
        （writer 分 57.3）但派活 prompt 无差异化，行为无矫正闭环。

        触发条件（同时满足）：
        1. agent-scores 中 writer 最近 2 条 history 均为负 delta
        2. 两条的 reason 至少一条命中表面修改关键词

        触发后动作：
        1. 解析最新 critic 报告的 critical/high 问题行（### [severity] 标题），
           逐条枚举进 prompt——不再依赖 writer 自行到报告中检索
        2. 强制要求输出「问题→处理结果」对照表，未修复项必须给出具体原因
        """
        import json as _json
        try:
            scores_path = _pl.PROJECT_ROOT / "memory" / "agent-scores.json"
            if not scores_path.exists():
                return ""
            scores = _json.loads(scores_path.read_text(encoding="utf-8"))
            history = (scores.get("writer", {}) or {}).get("history", [])
            if len(history) < 2:
                return ""
            recent2 = history[-2:]
            if not all(float(h.get("delta", 0)) < 0 for h in recent2):
                return ""
            reasons_text = " ".join(h.get("reason", "") for h in recent2)
            if not any(kw in reasons_text for kw in self._SURFACE_KEYWORDS):
                return ""
        except Exception:
            return ""

        # 解析最新 critic 报告的 critical/high 问题行
        issue_lines: list = []
        try:
            if critic_report_path:
                report = Path(critic_report_path)
                if report.exists():
                    for line in report.read_text(encoding="utf-8").split("\n"):
                        s = line.strip()
                        if not s:
                            continue
                        if "[critical]" in s.lower():
                            issue_lines.append(("critical", s.lstrip("# ").strip()[:120]))
                        elif "[high]" in s.lower():
                            issue_lines.append(("high", s.lstrip("# ").strip()[:120]))
                        if len(issue_lines) >= 12:
                            break
        except Exception:
            issue_lines = []

        header = (
            "\n\n【顽固升级警告（v6.9.28 程序化触发）】\n"
            "你已连续两轮被质量监督判定为表面修改/未实质修复（累积扣分中）。\n"
            "本轮不再是常规优化：以下 critical/high 问题逐条列出，你必须逐条处理。\n"
        )
        if issue_lines:
            header += "■ 本轮必须处理的问题清单（来自最新评审报告）：\n"
            for sev, text in issue_lines:
                header += f"  - [{sev.upper()}] {text}\n"
        else:
            header += (
                "■ 请打开评审报告，先列出其中全部 critical/high 问题编号，再逐条处理。\n"
            )
        header += (
            "■ 输出要求（硬性）：在修改说明末尾输出「问题→处理结果」对照表，\n"
            "  每行格式：问题编号 | 已修复（说明改动位置）/ 部分修复（说明剩余部分）/ 无法修复（写明具体障碍）。\n"
            "  缺少该对照表或存在未说明的跳过项，下一轮将被判定为顽固违规并继续重扣。\n"
        )
        return header

    # P1-2: 文献缺口检测和定向检索
    def _has_lit_gap(self, critic_result: Dict[str, Any]) -> bool:
        """检测 critic 是否指出了文献缺口。"""
        output = critic_result.get("output", "")
        gap_keywords = ["文献不足", "缺乏文献", "文献缺口", "缺少引用", "引用不足",
                        "支撑不足", "无文献", "需补充文献", "文献支撑", "缺乏近"]
        return any(kw in output for kw in gap_keywords)

    def _run_gap_identifier(
        self,
        proposal_id: str,
        prop_dir: Path,
        critic_result: Dict[str, Any],
        focus_section: Optional[Dict[str, str]],
        timeout: int = 120,
    ) -> Optional[Path]:
        """v6.7.7: 从 critic 报告中识别文献缺口，输出结构化 gap analysis。

        将 researcher 拆分为两步：
        1. gap_identifier（轻量，快速）：分析 critic 报告，提取需要补充文献的论点
        2. literature_searcher（重）：根据 gap analysis 执行定向检索

        Returns:
            gap analysis JSON 文件路径；失败返回 None
        """
        section_hint = f"聚焦章节：{focus_section['cn']}\n" if focus_section else ""
        critic_output = critic_result.get("output", "")[:3000]

        target_dir = prop_dir / "02_literature" / "gap-analysis"
        target_dir.mkdir(parents=True, exist_ok=True)
        import time as _t
        gap_path = target_dir / f"gap-analysis-r{int(_t.time())}.json"

        prompt = (
            f"请分析以下评审报告，识别需要补充文献支撑的具体缺口。\n\n"
            f"【课题】{proposal_id}\n"
            f"{section_hint}"
            f"【评审报告内容】\n{critic_output}\n\n"
            f"请执行：\n"
            f"1. 逐条阅读评审报告中指出的文献/引用/支撑不足问题\n"
            f"2. 对每个问题，明确：论点是什么、缺什么类型的文献、建议检索关键词\n"
            f"3. 忽略与文献无关的问题（如逻辑、格式等）\n"
            f"4. 输出严格的 JSON 文件到：{gap_path}\n"
            f"JSON 格式：\n"
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

        result = self._run_hermes("researcher", prompt, timeout)
        if result.get("success") and gap_path.exists():
            if _log:
                _log.info(f"[{proposal_id}] 文献缺口识别完成: {gap_path.name}")
            return gap_path
        else:
            if _log:
                _log.warning(f"[{proposal_id}] 文献缺口识别失败: {result.get('error', '')[:100]}")
            return None

    def _run_literature_searcher(
        self,
        proposal_id: str,
        prop_dir: Path,
        gap_path: Path,
        focus_section: Optional[Dict[str, str]],
        timeout: int = 300,
    ) -> Optional[Path]:
        """v6.7.11: 根据 gap analysis 执行定向文献检索（知识库优先 + 精确联网补充）。

        改造：通过 LiteratureService 统一检索/入库/状态查询。
        ⚠ v6.10.35 注：本函数不在 job 链主路径上——分步 job 链的 lit_search
        实际由 lifecycle/executor.py::_run_lit_search_step 执行（hermes agent
        loop 优先），本函数只被旧版单 job 兼容路径（_run_researcher_step）
        调用。多源补充/BibTeX 已同步维护于两处，修改检索逻辑时请核对
        executor 侧。

        Args:
            gap_path: _run_gap_identifier 生成的 JSON 文件路径

        Returns:
            lit-gap markdown 文件路径；失败返回 None
        """
        section_hint = f"聚焦章节：{focus_section['cn']}\n" if focus_section else ""

        target_dir = prop_dir / "02_literature" / "targeted-research"
        target_dir.mkdir(parents=True, exist_ok=True)
        import time as _t
        result_path = target_dir / f"lit-gap-{int(_t.time())}.md"

        # 改造：使用 LiteratureService 替换原有逻辑
        import json
        from literature_service import LiteratureService
        svc = LiteratureService()

        # 解析 gap 关键词
        try:
            gap_data = json.loads(gap_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            gap_data = {"gaps": []}
        gaps = gap_data.get("gaps", [])
        all_keywords = []
        for g in gaps:
            all_keywords.extend(g.get("search_keywords", []))
        gap_keywords = list(dict.fromkeys(all_keywords))[:10]  # 去重，最多 10 个

        # 1. 通过 LiteratureService.get_context() 获取本地知识库预检索结果
        kb_context = svc.get_context(gap_keywords=gap_keywords, proposal_id=proposal_id)

        # 2. 通过 LiteratureService.search() 执行联网检索
        papers = svc.search(keywords=gap_keywords, source="pipeline", proposal_id=proposal_id)

        # v6.8.44: 多源学术检索补充——在 hermes 联网检索基础上，
        # 叠加 OpenAlex（期刊论文）+ arXiv 检索结果，弥补单一 hermes 途径盲区。
        # 任一来源失败（限流/超时）不影响已有结果。
        # v6.10.31: 检索环节对齐整合能力——① 源扩展加 semantic_scholar
        # （search_academic 已并发化，墙钟不增加，失败自动容错）；② references
        # 聚焦轮启用 year_from 近 3 年过滤（呼应 critic 检查项"是否包含
        # 近 3 年文献"，补文献优先补新的）；③ 多源候选落 BibTeX 副产物，
        # writer 修订 references.md 时直接取标准格式条目（不再手编格式）。
        multi_source_papers = []
        bib_path: Optional[Path] = None
        # 默认值：try 块提前失败时报告标题不崩（v6.10.31）
        search_sources: tuple = ("arxiv", "openalex")
        year_from: Optional[int] = None
        try:
            import external_fetcher as ef
            # 将 gap 关键词组合为检索查询（取前 2 个关键词，避免超长查询触发 OpenAlex 限制）
            combined_query = " ".join(gap_keywords[:2]) if gap_keywords else "high harmonic generation"
            search_sources, year_from = _multi_source_search_config(focus_section)
            oa_papers = ef.search_academic(
                combined_query, max_results=5,
                sources=search_sources,
                year_from=year_from,
            )
            # 去重：与已有 hermes 检索结果对比（按 arxiv_id / doi / title）
            existing_keys = set()
            for p in papers:
                aid = p.get("arxiv_id", "")
                if aid:
                    existing_keys.add(f"arxiv:{aid}")
            for p in oa_papers:
                aid = p.get("arxiv_id", "")
                doi = (p.get("doi") or "").replace("https://doi.org/", "")
                title_key = p.get("title", "").strip().lower()[:80]
                key = f"arxiv:{aid}" if aid else (f"doi:{doi}" if doi else f"title:{title_key}")
                if key not in existing_keys:
                    existing_keys.add(key)
                    multi_source_papers.append(p)
            # BibTeX 副产物：候选文献标准引用格式（v6.10.31）
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

        # 3. 构建输出 markdown（保持与原来相同的文件路径和格式）
        lines = [
            f"# 定向文献检索报告\n",
            f"## 课题\n{proposal_id}\n",
        ]
        if section_hint:
            lines.append(f"## 聚焦章节\n{section_hint}\n")
        lines.append(f"## 检索关键词\n- {'、'.join(gap_keywords)}\n")
        lines.append(f"## 本地知识库预检索结果\n{kb_context}\n")
        lines.append(f"## 新增检索结果\n")
        for p in papers:
            arxiv_id = p.get("arxiv_id", "")
            title = p.get("title", "")
            authors = p.get("authors", "")
            year = p.get("year", "")
            score = p.get("score", 0.5)
            tldr = p.get("tldr", "")
            source_tag = "本地知识库" if not p.get("is_new", True) else "联网检索"
            lines.append(f"- {arxiv_id} | {title} | {authors} | {year} | {score} | {tldr} | 来源：{source_tag}")

        # v6.8.44: 多源学术检索结果（期刊论文 + 预印本）
        # v6.10.31: 标题按实际源动态生成 + 附 BibTeX 副产物路径
        if multi_source_papers:
            src_label = "+".join(search_sources)
            lines.append(f"\n## 多源学术检索补充（{src_label}）\n")
            if bib_path:
                lines.append(f"标准引用格式（可直接用于 references.md 修订）：{bib_path}\n")
            for p in multi_source_papers:
                aid = p.get("arxiv_id", "")
                doi = (p.get("doi") or "").replace("https://doi.org/", "")
                title = p.get("title", "")
                authors_list = p.get("authors", [])
                authors = ", ".join(authors_list[:3]) if isinstance(authors_list, list) else str(authors_list)
                year = p.get("year", "")
                venue = p.get("venue", "")
                cit = p.get("citation_count", 0)
                source_tag = p.get("source", "academic")
                # 期刊论文优先显示 DOI，预印本显示 arXiv ID
                ident = f"arXiv:{aid}" if aid else (f"DOI:{doi}" if doi else "无ID")
                abstract = (p.get("abstract") or "")[:150]
                lines.append(
                    f"- {ident} | {title} | {authors} | {year} | {venue} | "
                    f"引用:{cit} | 来源：{source_tag} | {abstract}"
                )

        result_path.write_text("\n".join(lines), encoding="utf-8")

        # v6.8.44: 多源检索有结果时也算成功（hermes 可能无结果但 OpenAlex 有期刊论文）
        total_papers = len(papers) + len(multi_source_papers)
        if total_papers:
            if _log:
                _log.info(
                    f"[{proposal_id}] 文献检索完成: {result_path.name} "
                    f"(hermes={len(papers)}, 多源={len(multi_source_papers)})"
                )
            return result_path
        else:
            if _log:
                _log.warning(f"[{proposal_id}] 文献检索未返回结果")
            return None

    def _build_kb_context_from_gap(
        self,
        gap_path: Path,
        proposal_id: Optional[str] = None,
        top_k_per_gap: int = 3,
        max_total: int = 15,
    ) -> str:
        """v6.7.11: 根据 gap analysis 预检索本地知识资产。

        改造：内部通过 LiteratureService.get_context() 实现，统一检索路径。

        Returns:
            结构化本地知识文本；失败返回提示语
        """
        try:
            import json
            gap_data = json.loads(gap_path.read_text(encoding="utf-8"))
            gaps = gap_data.get("gaps", [])
            if not gaps:
                return "（无预检索结果）"

            # 收集所有关键词
            all_keywords = []
            for g in gaps:
                all_keywords.extend(g.get("search_keywords", []))
            gap_keywords = list(dict.fromkeys(all_keywords))[:10]

            from literature_service import LiteratureService
            svc = LiteratureService()
            return svc.get_context(gap_keywords=gap_keywords, proposal_id=proposal_id)
        except Exception as e:
            if _log:
                _log.warning(f"知识库预检索失败: {e}")
            return "（知识库预检索失败，请联网检索补充）"

    def _run_researcher_targeted(
        self,
        proposal_id: str,
        prop_dir: Path,
        critic_result: Dict[str, Any],
        focus_section: Optional[Dict[str, str]],
        timeout: int = 300,
    ) -> str:
        """v6.7.7: researcher 入口——先识别缺口，再执行检索，保持单 job 节奏。

        内部拆分为 _run_gap_identifier + _run_literature_searcher，
        但对外仍是一个 job 调用，避免 worker cron 节奏变慢。
        """
        # 第一步：识别缺口（轻量，默认 300s）
        gap_path = self._run_gap_identifier(
            proposal_id, prop_dir, critic_result, focus_section, timeout=300
        )
        if not gap_path:
            return ""

        # 第二步：执行检索（重量，剩余超时）
        result_path = self._run_literature_searcher(
            proposal_id, prop_dir, gap_path, focus_section, timeout=max(timeout - 300, 180)
        )
        if result_path:
            # v6.7.10: 自动将检索结果导入文献阅读笔记
            try:
                from literature_notes import LiteratureNotes
                ln = LiteratureNotes(prop_dir)
                imported = ln.import_from_report(result_path)
                if _log and imported:
                    _log.info(f"[{proposal_id}] 已导入 {imported} 条文献阅读笔记")
            except Exception as e:
                if _log:
                    _log.warning(f"[{proposal_id}] 导入文献阅读笔记失败: {e}")
            return f"\n【文献补充（researcher 定向检索）】\n请参考 {result_path} 中的新文献，在修订时引用。\n"
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
        missing_sections: Optional[List[str]] = None,
        ai_check_result: Optional[Dict[str, Any]] = None,
        round_num: int = 0,  # v6.10.26: section 感知读 critic 报告所需轮次
        params_supplement: str = "",  # v7.2.13: 数值口径表注入块
    ) -> Dict[str, Any]:
        """派活给 writer profile 根据评审意见优化申请书。

        P0-2: 聚焦最弱维度，针对性改进。
        P1-1: 支持章节级修订（focus_section）。
        v6.7.7: 章节级修订只写入对应 section 文件，再自动组装 proposal-draft.md。
        """
        sections = ProposalSections(prop_dir / "04_proposal")
        sections.ensure_split()
        standards_path = str(self.standards_path.relative_to(_pl.PROJECT_ROOT))
        # 找最新的 critic 报告
        # v6.10.26: section 感知——优先取本轮聚焦章节自己的报告
        # （critic-round-{n}-{section}.md），杜绝误取同轮其他 section
        # 的报告（旧逻辑按文件名倒序取"最新"，r5 起后缀报告与裸报告并存，
        # 字母序倒序会把 references 报告当 rationale 报告喂给 writer）。
        # round_num 由调用方传入（v6.10.26 新增参数），缺失时回退旧逻辑。
        review_dir = prop_dir / "05_review"
        critic_reports = sorted(review_dir.glob("critic-round-*.md"), reverse=True)
        latest_critic = str(critic_reports[0]) if critic_reports else ""
        _focus_key = focus_section.get("key") if focus_section else (
            "full_review" if is_full_review else ""
        )
        if _focus_key and round_num:
            _sec_report = _critic_report_path(prop_dir, round_num, _focus_key)
            if _sec_report.exists():
                latest_critic = str(_sec_report)
        # v6.9.60: 大体量 critic 报告 digest——实测报告 16-37KB 无篇幅约束，
        # writer 每轮读全文是超时输入大头。超阈值（25KB）时程序化提取
        # 问题结构（severity 行/标题/评分）生成 ≤8KB digest 供读取，
        # 完整报告路径在 digest 头部注明（需要语境时可回查）。
        try:
            from proposal_lifecycle.section_hygiene import build_critic_digest
            _digest = build_critic_digest(Path(latest_critic)) if latest_critic else None
            if _digest:
                latest_critic = str(_digest)
        except Exception:
            pass

        # P0-2: 构建维度聚焦提示
        dim_focus = ""
        if weakest_dim and dim_scores:
            dim_cn = {"innovation": "创新性", "feasibility": "可行性", "rigor": "严谨性", "expression": "表达质量", "completeness": "完整性"}
            weakest_cn = dim_cn.get(weakest_dim, weakest_dim)
            dim_scores_str = "、".join(f"{dim_cn.get(k,k)} {v:.2f}" for k, v in dim_scores.items())
            dim_focus = (
                f"\n【维度评分（本轮聚焦）】\n"
                f"各维度：{dim_scores_str}\n"
                f"⚠️ 最弱维度：{weakest_cn}（{dim_scores[weakest_dim]:.2f}）\n"
                f"请优先改进 {weakest_cn} 相关的问题，这是本轮的聚焦重点。\n"
            )

        # v6.7.7: 构建写入目标与读取文件列表
        # v6.9.46: 输入与目标对齐——旧版无条件列出全部 5 个章节文件
        # （最大 ~180KB）供 writer "可读"，但章节级修订指令又说"只修改
        # 聚焦章节"，输入与目标不匹配是 writer 超时的主因之一（4 次）。
        # 章节级修订且无跨章节 P0 时只列聚焦章节；整体修订/跨章节修复
        # 时保留全列表（references.md 仍排除——修订引用走 references 专轮）。
        _allow_cross = bool(
            focus_section
            and any(
                isinstance(e, dict) and e.get("round_resolved") is None and not e.get("stale")
                for e in (self._load_open_critical_issues(proposal_id) or [])
            )
        )
        if focus_section and not _allow_cross:
            writer_read_files = [
                str(prop_dir / "04_proposal" / "sections" / f"{focus_section['key']}.md")
            ]
        else:
            writer_read_files = [
                str(prop_dir / "04_proposal" / "sections" / f"{s['key']}.md")
                for s in PROPOSAL_SECTIONS
                if sections.section_exists(s['key'])
                and s['key'] != "references"  # v6.9.46: 引用修订走专轮
            ]

        # v6.7.10: 构建缺失模块提示
        section_key_to_cn = {s["key"]: s["cn"] for s in PROPOSAL_SECTIONS}
        missing_cn = [section_key_to_cn.get(k, k) for k in (missing_sections or [])]
        missing_hint = ""
        if missing_cn:
            missing_hint = (
                f"\n【缺失模块必须补齐】当前申请书还缺少以下模块：{', '.join(missing_cn)}。\n"
                f"若本轮聚焦章节在缺失列表中，请先生成完整内容；\n"
                f"若其他缺失模块已有相关素材（如研究方案中包含预期成果描述），请拆分并补充独立文件。\n"
            )

        # 四大产物路径
        research_idea_path = prop_dir / "00_research_idea.md"
        methodology_manual_path = prop_dir / "03_method" / "method-manual.md"
        reading_notes_path = prop_dir / "02_literature" / "reading-notes.md"

        if focus_section:
            target_section_file = prop_dir / "04_proposal" / "sections" / f"{focus_section['key']}.md"
            section_focus = (
                f"\n【本轮聚焦章节】{focus_section['title']}\n"
                f"请只修改该章节文件：{target_section_file}\n"
                f"不要修改其他章节文件。\n"
                f"修改完成后，将优化后的完整章节内容覆盖写入 {target_section_file}\n"
                f"系统会自动根据章节文件重新组装 proposal-draft.md。\n"
            )
            # v6.8.22: 断裂点4——存在未解决 P0 时放宽章节限制，允许跨章节修复
            try:
                unresolved_p0 = [
                    e for e in self._load_open_critical_issues(proposal_id)
                    if isinstance(e, dict) and e.get("round_resolved") is None and not e.get("stale")
                ]
                if unresolved_p0:
                    cross_sections = sorted({e.get("section", "?") for e in unresolved_p0})
                    section_focus += (
                        f"\n【例外：历史遗留 P0 跨章节修复】\n"
                        f"当前存在 {len(unresolved_p0)} 条未解决的 critical/high 问题，"
                        f"涉及章节：{', '.join(cross_sections)}。\n"
                        f"为消除这些 P0，你可以一并修改上述涉及章节文件（即使不在本轮聚焦章节内），"
                        f"但每次改动必须与聚焦章节问题直接相关，避免无关大改。\n"
                    )
            except Exception:
                pass
            primary_read = str(target_section_file)
        elif is_full_review:
            target_section_file = None
            # v6.9.53: full_review.md 语义重定义——只写"全文逻辑骨架"。
            # 08-27 实证：writer 把一致性核查记录（round-N 修复确认表、
            # 逐项对照）当正文写入 full_review.md，膨胀到 25-33KB——
            # 真实 NSFC 申请书没有"整体一致性审查"章节，该文件是派生索引。
            section_focus = (
                f"\n【本轮为整体一致性修订】\n"
                f"请只做章节间的衔接、术语统一、冗余删减，不要大幅改动内容。\n"
                f"可修改任意章节文件（在 {prop_dir}/04_proposal/sections/ 下），\n"
                f"但请保持各章节文件独立，系统会自动组装 proposal-draft.md。\n\n"
                f"■ full_review.md 写法（v6.9.53 起严格执行）：\n"
                f"该文件只保留'全文逻辑骨架'，三部分、总篇幅 ≤3000 字：\n"
                f"  ① 主线论证链（3-5 句：核心问题→研究内容→方案如何回应）\n"
                f"  ② 章节衔接点（立项依据→研究内容→研究方案的关键承接关系）\n"
                f"  ③ 跨章节统一口径表（关键指标/术语的唯一口径）\n"
                f"一致性核查的过程性材料（逐项对照、处置记录、轮次说明）\n"
                f"一律写入 {prop_dir}/05_review/ 下的报告文件，严禁进入章节文件。\n"
                f"本轮的实际修订落在 rationale/content/scheme 三个正文文件，\n"
                f"full_review.md 只更新骨架使其与正文一致。\n"
            )
            primary_read = str(prop_dir / "04_proposal" / "proposal-draft.md")
        else:
            target_section_file = None
            section_focus = ""
            primary_read = str(prop_dir / "04_proposal" / "proposal-draft.md")

        # v6.8.6: 强化叙述式写作风格要求 + 去AI味 + 范本对标
        # v6.9.53: writer 侧章节卫生注入。
        # v6.9.55: 质量核心重构——质量指令（具体冗余/无关位置）为主，
        # 体量参考为辅（纯信息，不含"净删 N 字"式字数指令——字数是
        # 症状，冗余/无关才是病因）。
        try:
            writer_budget_text = budget_report_text(
                prop_dir / "04_proposal" / "sections",
                focus_key=(focus_section["key"] if focus_section else None),
            )
        except Exception:
            writer_budget_text = ""
        try:
            writer_quality_text = quality_directives_text(
                prop_dir,
                focus_key=(focus_section["key"] if focus_section else None),
            )
        except Exception:
            writer_quality_text = ""

        # v7.0.0: writer 侧写作风格知识（叙述式规则/去AI味/指标红线）已收敛
        # 至 .hermes/skills/nsfc-writing/SKILL.md 二/三/四/八节，经
        # _load_nsfc_writing_skill_text('writer') 在 prompt 拼接处注入。
        # v7.0.4: 首句叙述式总纲与 skill 四节重复，删除（单一真相源）；
        # 范本定位按 v7.0.2 用户裁决对齐——范本是语体参考，不锚定内容深度。
        narrative_requirement = (
            "\n【写作风格要求（对照范本 references/nsfc-templates/，详见 prompt 内 skill 注入块）】\n"
            "撰写/修改前请先阅读范本文件，以范本为语体参考（深度不锚定范本，"
            "操作细节不因范本未写而省略）。\n"
            "方法学手册才是细节（公式/参数表/步骤）的归属地，申请书重思路重论证。\n"
            "如果评审报告已指出 narrative/anti-AI 问题，必须优先重写为连贯叙述。\n"
        )

        # v6.8.7: 程序化 AI 检测结果——writer 必须修复检测到的 AI 模式问题
        # v6.9.47: 附逐词量化清单（词→当前次数→目标），修复指令从"不可执行"
        # 变为"可量化达成"；白名单术语已在计数前剔除，writer 无需处理
        ai_check_text = ""
        if ai_check_result and ai_check_result.get("top_issues"):
            ai_check_text = (
                f"\n【程序化 AI 写作模式检测结果（必须修复）】\n"
                f"表达质量天花板：{ai_check_result['ceiling']:.2f}"
                f"（原始扣分后 {ai_check_result.get('raw_ceiling', ai_check_result['ceiling']):.2f}）\n"
                f"当前天花板{'低于 0.7，属于严重 AI 味' if ai_check_result['ceiling'] < 0.7 else '在 0.7 以上，但仍有改进空间'}。\n"
                f"检测到的问题：\n"
            )
            for issue in ai_check_result["top_issues"]:
                ai_check_text += f"  - {issue}\n"

            # v6.9.47: 逐词量化清单（当前次数 → 目标阈值）
            details = ai_check_result.get("details") or {}
            redundant = details.get("redundant_modifiers") or {}
            transition = details.get("transition_words") or {}
            if redundant.get("found"):
                ai_check_text += (
                    f"\n冗余修饰词逐词清单（已剔除'关键科学问题/系统误差/有效性'等"
                    f"法定术语，以下为真实冗余用法，必须逐词削减）：\n"
                )
                thr = redundant.get("threshold", 12)
                for w, c in sorted(redundant["found"].items(), key=lambda x: -x[1]):
                    if c > 0:
                        ai_check_text += f'  - "{w}" 当前 {c} 次 → 削减至 ≤{max(1, thr // 3)} 次\n'
            if transition.get("found"):
                ai_check_text += "\n死板关联词逐词清单（用内容驱动衔接替代）：\n"
                for w, c in sorted(transition["found"].items(), key=lambda x: -x[1]):
                    if c > 0:
                        ai_check_text += f'  - "{w}" 当前 {c} 次 → 减半或替换衔接方式\n'

            ai_check_text += (
                f"\n你必须在本次修改中优先解决上述 AI 模式问题：\n"
                f"  - 死板关联词 → 用内容驱动衔接替代（进而、据此、理解…后、确立后）\n"
                f"  - 模板句式'为...提供...' → 改为具体动词（保障、确立、对接、满足、形成）\n"
                f"  - 模板主语'本项目拟/将' → 删除，直接以动词或内容词开头\n"
                f"  - 冗余修饰 → 按上方逐词清单逐处删除或换具体表述\n"
                f"  - 超长句 → 拆分为短句（<60字）\n"
                f"  - 元话语 → 删除，直接陈述科学事实\n"
                f"  - 过度加粗 → 删除加粗标记，范本中几乎不用\n"
                f"  - 编号列表 → 改为连贯叙述式段落\n"
                f"注意：白名单术语（'关键科学问题''系统误差''有效性''同时电离'等）是科研法定用法，"
                f"无需修改，也不计入扣分。\n"
                f"修改后，每个段落与 benchmark_anchors 中的范本锚点段落对比，确保语体和论证密度达标。\n"
            )

        # v6.10.41: 文件纯净性红线按章节裁剪——旧实现把 references 工作日志
        # 迁移规则、full_review 骨架规则等全量注入每次 writer 会话（不分
        # 章节，~2K 字符/次的无效指令）。裁剪：通用规则始终注入，
        # references/full_review 专属规则只在对应轮注入。
        _eff_section = (focus_section or {}).get("key", "") or (
            "full_review" if is_full_review else ""
        )
        # v7.0.0: 文件纯净性红线与内容边界已收敛至 nsfc-writing skill
        # 六节（含 references/full_review 专属子条），内容质量纪律收敛至
        # 七节。代码只保留章节裁剪提示（专属条目对应轮高亮）。
        # v7.0.4: 删除与 skill 六节逐条重复的旧全量内联（references/
        # full_review 迁移规则、内容边界红线——审计发现注释声称已收敛
        # 但代码仍内联全文，三写冗余）。
        _purity_rules = _load_nsfc_writing_skill_text('purity')
        if _eff_section == "references":
            _purity_rules += (
                "\n■ 本轮为 references 轮：skill 六节第 3 条（references 专属）"
                "为本轮重点，历史遗留的映射表/核实声明务必迁出。\n"
            )
        if _eff_section == "full_review":
            _purity_rules += (
                "\n■ 本轮为 full_review 轮：skill 六节第 4 条（full_review "
                "专属）为本轮重点，骨架 ≤3000 字。\n"
            )

        # v7.2.19（用户裁决「执行」对策 2）: references 轮引用强制对照纪律——
        # houston/ssh 实证 writer 凭记忆转录文献产生"系统性作者链杜撰"
        # （真题真 ID 换作者链，houston 31 条中 8 critical；ssh 扩容 35→42
        # 引入新虚构）。检索池里有正确记录但 writer 不看——堵源头。
        _refs_discipline = ""
        if _eff_section == "references":
            _refs_discipline = (
                "\n【引用真实性强制对照（零容忍红线）】\n"
                "1. 每条文献条目（作者链/标题/期刊/卷期页/DOI/arXiv ID）必须"
                "逐字段对照检索池真实记录誊写——池源：02_literature/"
                "targeted-research/lit-gap-*.md 检索结果、candidates-*.bib "
                "标准条目、02_literature/reading-notes.md 已核实笔记。\n"
                "2. 禁止凭记忆生成或改写任何文献条目字段；池中无对应记录的"
                "条目一律不得写入（宁可少一条，不可编一条）。\n"
                "3. 写入后自查：逐条确认作者顺序、姓氏缩写、年份、卷页与池"
                "记录一致。\n"
                "违反此红线按 critical 计（rigor 清单③文献支撑真实——不过）。\n"
            )

        prompt = (
            f"请根据对抗评审意见优化申请书。\n\n"
            f"【主读取文件】{primary_read}\n"
            f"【章节文件】\n" +
            "\n".join(f"- {p}" for p in writer_read_files) + "\n\n"
            f"【项目类型】{project_type}\n"
            f"【质量标准】请读取 {standards_path}，重点关注：\n"
            f"  - section_standards（每个 section 的详细撰写要求，必须逐条对标）\n"
            f"  - programmatic_checks（程序化检测规则，了解哪些模式会被扣分）\n"
            f"  - writing_style_rules.anti_ai_patterns（去AI味量化阈值；文字规范见 prompt 内 skill 注入块）\n"
            f"  - indicator_red_lines（指标红线）\n"
            f"  - content_boundaries（内容边界）\n"
            f"  - general_principles.scoring_rubric（评分档位标准，写作时对标目标档位≥0.9）\n"
            f"  - reference_materials.style_benchmark（范本写作标杆摘要）\n"
            f"  - reference_materials.benchmark_anchors（范本锚点段落，写作时模仿其语体和论证密度）\n"
            f"  - general_principles.scope_exclusion（范围排除：不撰写研究基础/工作条件/团队/经费内容）\n"
            f"【评审报告】{latest_critic}\n"
            f"{dim_focus}"
            f"{section_focus}"
            f"{missing_hint}"
            f"{lit_supplement}"
            f"{_refs_discipline}"
            f"{params_supplement}"
            f"{ai_check_text}\n"
            f"{narrative_requirement}\n"
            f"请执行：\n"
            f"1. 读取主读取文件（章节级修订只读聚焦章节，整体修订可读全部章节）\n"
            f"2. 读取评审报告中的所有问题\n"
            f"3. 逐条解决每个问题（按严重程度优先）\n"
            f"4. 重点改进最弱维度相关的问题\n"
            f"5. 如果评审报告存在 narrative/list-style 类问题，必须将对应段落重写为连贯叙述式论述\n"
            f"6. 只修改聚焦章节文件（或整体衔接涉及的章节文件），保持其他章节不变（增量优化）\n"
            f"7. 将优化后的内容覆盖写入对应章节 .md 文件（不是 proposal-draft.md）\n"
            f"8. 补齐缺失模块：若当前聚焦章节或 missing 列表中的模块为空，必须生成完整内容\n"
            f"9. 同步更新产物：\n"
            f"   a) 课题设想：{research_idea_path}\n"
            f"      若研究内容、技术路线、创新点有重大调整，同步更新课题设想对应部分。\n"
            f"   b) 文献阅读笔记：{reading_notes_path}\n"
            f"      若本轮使用了新文献（尤其是 {lit_supplement[:80] if lit_supplement else '定向检索结果'}），\n"
            f"      请在笔记中追加一条记录：阅读日期、文献标题、来源、核心结论、与课题关联、已引用位置。\n"
            f"   c) 方法学手册：不由本步骤更新（v6.9.60 单一真相源治理）——\n"
            f"      方法学手册唯一真相源为 03_method/method-manual.md，由轮末专职\n"
            f"      update_method_manual 步骤统一维护，writer 不得直接写该文件\n"
            f"      （双写曾是手册分裂膨胀的根源）。\n\n"
            f"{_purity_rules}"
            f"{_load_nsfc_writing_skill_text('writer')}"
            f"{writer_quality_text}"
            f"{writer_budget_text}"
        )

        # v6.8.17: cross-proposal 范例注入——从最高分课题提取范例段落
        # v6.8.19 修复: section_key 必须从 focus_section 派生（原版直接引用未定义变量，
        # 导致 writer 每次必抛 NameError，4h 内 5 个 writer job 全失败）
        if focus_section:
            section_key = focus_section.get("key", "")
        elif is_full_review:
            section_key = "full_review"
        else:
            section_key = ""

        # v6.10.0（T3）：方法学专题参考注入——scheme 聚焦轮按课题
        # 关键词匹配方法页（已验证方法+参数依据），支撑研究内容与
        # 可行性论证；开关与页数/字数上限由 methods-inject.json 控制
        _methods_block = ""
        if section_key == "scheme":
            _methods_block = _load_methods_reference_block(
                self, proposal_id, prop_dir)

        _exemplar_block = _load_cross_proposal_exemplar(self, proposal_id, section_key)
        if _exemplar_block:
            prompt += _exemplar_block
        if _methods_block:
            prompt += _methods_block

        # v6.8.22: 注入未解决 P0 列表（断裂点2）——writer 必须优先消除历史遗留 P0
        _p0_memory = self._build_p0_memory_text(proposal_id, exclude_resolved=False)
        if _p0_memory:
            prompt += (
                _p0_memory
                + "请将上述状态为'待解决'的历史遗留 P0 问题列为最高优先级处理：\n"
                + "  - 逐条分析各问题在当前申请书中的体现，针对性修改对应章节\n"
                + "  - 修改后请明确说明每个待解决问题的处理结果（已消除 / 已缓解 / 无法处理及原因）\n"
                + "即使该问题归属章节不是本轮聚焦章节，只要严重影响质量，也应一并修复。\n"
                + "状态为'已解决'的问题请保持现状，不要为了改而改导致质量回退。\n"
            )
        # v7.2.62: 复发问题升级通道（自迭代环②快速路径，每轮生效）——
        # 曾被标记解决又被复见的问题 = 修复动作引入新伤的打地鼠签名。
        # 旧升级通道需「连续两轮 monitor 负 delta」才触发（周级延迟），
        # 本通道由问题账本的 recurrence_count 直接驱动（轮级延迟）。
        _recurrence_block = self._build_recurrence_escalation_text(proposal_id)
        if _recurrence_block:
            prompt += _recurrence_block

        # v7.2.67: PaperQA2 式证据协议注入——scheme/references/full_review 轮
        # 把「检索-取证-挂引用」变成写作前置纪律（rationale/content 轮返回
        # 空串避免 prompt 膨胀；enforcement 既有：critic references 轮三池
        # 红线 + params 口径校验，本块补生成端源头）。
        _evidence_block = self._build_evidence_protocol_block(
            proposal_id, prop_dir, section_key)
        if _evidence_block:
            prompt += _evidence_block

        # v6.8.18: 注入 agent 分数反馈
        _writer_score_feedback = self._load_agent_score_feedback("writer")
        if _writer_score_feedback:
            prompt += _writer_score_feedback

        # v6.9.28: writer 顽固升级——连续两轮表面修改时强制逐条响应
        _escalation_block = self._build_writer_escalation_block(latest_critic)
        if _escalation_block:
            prompt += _escalation_block

        # v6.8.27: Writer 侧注入人工审核反馈（之前只有 critic 侧注入）
        # 避免 writer 重复犯人工审核已指出的问题
        _writer_human_feedback = self._load_human_feedback_block(proposal_id)
        if _writer_human_feedback:
            prompt += "\n\n## 历史人工审核反馈\n\n以下为人工审核曾指出的问题，请在本次修改中避免重蹈覆辙：\n" + _writer_human_feedback

        result = self._run_hermes("writer", prompt, timeout)

        # v6.7.7: writer 返回后，自动从 sections/ 重新组装 proposal-draft.md
        if result.get("success"):
            try:
                sections.assemble_draft()
                if _log:
                    _log.info(f"[{proposal_id}] 已从 sections/ 重新组装 proposal-draft.md")
            except Exception as e:
                if _log:
                    _log.warning(f"[{proposal_id}] 组装 proposal-draft.md 失败: {e}")

        return result

    def _sync_derivative_artifacts(
        self,
        proposal_id: str,
        prop_dir: Path,
        timeout: int = 300,
    ) -> Dict[str, Any]:
        """v6.7.11: 根据最新申请书同步更新课题设想、方法学手册、文献阅读笔记。

        只在 full_review 轮调用，避免每轮都增加 hermes 开销。
        """
        research_idea_path = prop_dir / "00_research_idea.md"
        # v6.9.60: 方法学手册单一真相源——03_method/method-manual.md
        # （此前 04_proposal/methodology-manual.md 与其双写分裂）
        methodology_manual_path = prop_dir / "03_method" / "method-manual.md"
        reading_notes_path = prop_dir / "02_literature" / "reading-notes.md"
        proposal_path = prop_dir / "04_proposal" / "proposal-draft.md"

        # 确保目录存在
        reading_notes_path.parent.mkdir(parents=True, exist_ok=True)

        # 读取现有内容长度，判断是否跳过
        ri_len = len(research_idea_path.read_text(encoding="utf-8").strip()) if research_idea_path.exists() else 0
        mm_len = len(methodology_manual_path.read_text(encoding="utf-8").strip()) if methodology_manual_path.exists() else 0
        rn_len = len(reading_notes_path.read_text(encoding="utf-8").strip()) if reading_notes_path.exists() else 0

        # 如果课题设想已经比较完整（>2000字符）且方法学手册也完整（>5000字符），则跳过
        if ri_len > 2000 and mm_len > 5000:
            return {"success": True, "skipped": True, "reason": "课题设想和方法学手册已较完整"}

        prompt = (
            f"请根据最新申请书，同步更新以下三个配套文件。\n\n"
            f"【申请书】{proposal_path}\n"
            f"【现有课题设想】{research_idea_path}（当前 {ri_len} 字符）\n"
            f"【现有方法学手册】{methodology_manual_path}（当前 {mm_len} 字符）\n"
            f"【现有文献阅读笔记】{reading_notes_path}（当前 {rn_len} 字符）\n\n"
            f"更新要求：\n"
            f"1. {research_idea_path}：课题设想。包含标题、研究背景与动机、现存研究空白/瓶颈、拟开展研究内容和方案、拟采用技术路线、创新点。基于申请书提炼，不添加申请书中未出现的内容。\n"
            f"   **重要约束（v6.8.27）**：本次更新仅限同步申请书已有内容，"
            f"不允许新增科学目标或改变研究方向。如需方向性调整，应在报告中标注"
            f"'需要退回研究设想评审'，由系统触发 idea_review。\n"
            f"2. {methodology_manual_path}：方法学手册。重方法细节（公式推导/参数表/技术路线图/局限性/误差分析）。若已较完整，只补充申请书新增或调整部分对应的方法细节。\n"
            f"3. {reading_notes_path}：文献阅读笔记。若申请书引用了新文献而笔记中未记录，请按时间倒序追加一条记录，包含：阅读日期、文献标题、来源、核心结论、与课题关联、已引用位置。\n\n"
            f"请直接覆盖写入对应文件，不需要在 stdout 中输出全文。"
        )

        result = self._run_hermes("writer", prompt, timeout)
        return result

    def _run_hermes(self, profile: str, prompt: str, timeout: int) -> Dict[str, Any]:
        """执行 hermes oneshot。

        v6.8.3-fix9: 使用 Popen + 进程组杀死替代 subprocess.run，
        确保 timeout 后 hermes CLI 及其子进程被彻底清理。
        subprocess.run(timeout=N) 在 macOS 上只 kill 直接子进程，
        如果 hermes CLI fork 了额外进程（如 gateway worker），
        这些进程会继续运行导致 CLI 端口/管道不释放，Python 侧永远收不到子进程退出信号。
        """
        env = hermes_subprocess_env()
        # v6.9.68: 提前 hermes 自身 stale 放弃阈值。默认需 5 次连续静默挂起
        # 才触发 give-up（error_classifier 7b 分支 → should_fallback=True →
        # hermes 按 fallback 链切换供应商），而 api_max_retries=3 结构性达不到；
        # 且 3×300s(大上下文 stale)=900s 恰好等于 CoPilot 击杀线，进程死在
        # 重试循环中途连报错都来不及输出（08-27/28 实证：9 个终态 job 全为
        # 超时+零输出+零 429 文本）。降为 2 次让 give-up 在击杀前发生，
        # hermes 得以按自身链降级（与 CoPilot 侧模型逃生双保险）。
        env.setdefault("HERMES_STREAM_STALE_GIVEUP", "2")

        import time
        import signal
        cmd = ["hermes", "--profile", profile, "-z", prompt]
        # v6.9.68: 模型逃生——主模型静默挂起（长输出连续超时→熔断器判定）
        # 时强制本次调用走备用模型。hermes 内部降级只认明确报错（429/
        # billing 等 FailoverReason），静默挂起归为同供应商重试，编排层
        # 注入是唯一出路。试探窗口内返回 None（本次走主模型试探）。
        try:
            from circuit_breaker import escape_override_target
            _esc_target = escape_override_target(profile=profile)
        except Exception:
            _esc_target = None
        if _esc_target:
            cmd += ["--provider", _esc_target["provider"], "-m", _esc_target["model"]]
            if _log:
                _log.info(
                    f"[model-escape] {profile} 强制备用模型: "
                    f"{_esc_target['provider']}/{_esc_target['model']}"
                )
        t0 = time.time()
        proc = None
        try:
            # start_new_session=True 使子进程成为新进程组的 leader
            # 超时/挂起后可以用 os.killpg 杀死整个进程组
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env=env, cwd=str(_pl.PROJECT_ROOT),
                start_new_session=True,
            )
            # v6.9.84: 活性感知通信替代 communicate(timeout)——
            # 慢而在跑（持续产出）等到硬上限不被砍；零输出挂起
            # （zai 限流形态）在 HERMES_STALL_TIMEOUT_S 内快速击杀，
            # error 标记 stall 供熔断/逃生更快接管。超时上限不再承担
            # "猜一个足够大的时间"的职责（08-31 用户裁决：治本而非
            # 无限制提升超时）。
            com = _communicate_with_stall(proc, timeout)
            stdout, stderr = com["stdout"], com["stderr"]
            if com["stall"]:
                if _log:
                    _log.warning(
                        f"hermes 零输出挂起 {com['stall_seconds']}s，"
                        f"快速击杀（总耗时 {com['elapsed_s']}s < 上限 {timeout}s）"
                    )
                return {
                    "success": False, "output": "",
                    "error": f"超时(挂起{com['stall_seconds']}s零输出)",
                    "elapsed_s": com["elapsed_s"],
                }
            if com["timeout"]:
                return {
                    "success": False, "output": "",
                    "error": f"超时({timeout}s)",
                    "elapsed_s": com["elapsed_s"],
                }
            elapsed = com["elapsed_s"]
            if proc.returncode == 0:
                output = stdout.strip()
                if len(output) > 50000:
                    output = output[:50000] + f"\n... (截断，共{len(output)}字符)"
                # v6.8.46: API 错误检测——配额耗尽/限流时 hermes CLI returncode 仍为 0，
                # stdout 是错误文本。若不拦截，垃圾文本会被解析成伪分数污染 score_history
                # （实例：2026-08-14 MiniMax Token Plan 耗尽，429 错误文本被解析成 0.18 分）
                err_sig = _detect_api_error(output)
                if err_sig:
                    if _log:
                        _log.warning(
                            f"hermes 返回 API 错误({err_sig})，标记 success=False: {output[:120]}"
                        )
                    return {
                        "success": False, "output": output[:2000],
                        "error": f"api_error:{err_sig}", "elapsed_s": elapsed,
                    }
                return {"success": True, "output": output, "elapsed_s": elapsed}
            return {
                "success": False, "output": stdout[:2000],
                "error": stderr[:500], "elapsed_s": elapsed,
            }
        except Exception as e:
            # 兜底：确保进程被清理
            if proc and proc.poll() is None:
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                except Exception:
                    pass
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

    def _apply_anchor_conclusion_binding(
        self,
        proposal_id: str,
        critic_text: str,
        dim_scores: Dict[str, float],
        score_after: float,
        project_type: str,
    ) -> float:
        """v6.9.25: 锚点对比结论与评分档位强制绑定——范本锚点成为分数锚。

        背景：锚点对比此前只是格式门槛（有该段落即可），对比结论与打分
        无量化绑定，"与范本差距明显"照样可打 0.8（08-18 实测）。绑定
        规则与 critic prompt 中声明的档位一致，自评超限时程序强制修正。
        结论缺失（旧格式报告）时不做绑定，保持兼容。
        """
        anchor_conclusion = self._extract_anchor_conclusion(critic_text)
        if not anchor_conclusion:
            return score_after

        expr_cap, overall_cap = {
            "差距明显": (0.69, 0.84),
            "基本接近": (0.79, 0.89),
            "达标": (None, None),
        }[anchor_conclusion]

        if (
            expr_cap is not None
            and "expression" in dim_scores
            and dim_scores["expression"] > expr_cap
        ):
            if _log:
                _log.warning(
                    f"[{proposal_id}] 锚点结论[{anchor_conclusion}]绑定：表达质量 "
                    f"{dim_scores['expression']:.2f} > {expr_cap:.2f}，强制 cap"
                )
            dim_scores["expression"] = expr_cap
            score_after = min(
                score_after, self._recalculate_score(dim_scores, project_type)
            )
        if overall_cap is not None and score_after > overall_cap:
            if _log:
                _log.warning(
                    f"[{proposal_id}] 锚点结论[{anchor_conclusion}]绑定：综合分 "
                    f"{score_after:.2f} > {overall_cap:.2f}，强制 cap"
                )
            score_after = overall_cap
        return score_after

    def _extract_anchor_conclusion(self, critic_text: str) -> str:
        """v6.9.25: 从 critic 报告中提取锚点对比结论行。

        识别格式：`锚点对比结论：达标|基本接近|差距明显`（critic prompt
        v6.9.25 起强制要求）。无明确结论行时返回空串（不做档位绑定，
        保持旧报告兼容）。
        """
        if not critic_text:
            return ""
        import re
        m = re.search(
            r"锚点对比结论[：:]\s*(达标|基本接近|差距明显)", critic_text
        )
        return m.group(1) if m else ""

    def _extract_score(self, critic_result: Dict[str, Any]) -> float:
        """从 critic 输出中提取综合评分。

        v7.2.8 修复（健康检查发现）：critic 在评分档位依据小节会写出
        公式推演「综合评分：0.35×0.84＋0.29×0.80…＝0.785 → 0.79」，
        原 re.search 取第一个匹配会把权重值 0.35 当成综合分，污染 score_history。
        修复：检测到「综合评分：x.xx」后跟 × * + ＝ 等算术/公式字符时跳过该候选，
        在所有候选中选最后一个真正行尾/独立成行的综合分；若无干净候选，
        回退加权维度计算。

        实例：moire r8 full_review 09-30 02:39 BJT 被误提 0.35（实际 0.79），
        触发 monitor score_drop 告警。详见 healthcheck 09-30 08h。
        """
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
        # v7.2.8: 收集所有候选，公式行（后跟 × * + ＝ → 等）一律跳过
        _FORMULA_CHARS = ("×", "*", "+", "＝", "=", "→", "*", "·")
        for pattern in patterns:
            clean_candidate = None
            for m in re.finditer(pattern, output, re.IGNORECASE):
                val = m.group(1)
                end = m.end()
                tail = output[end:end + 4].lstrip()
                # 公式行：紧跟 × * + ＝ = → 等算术/推导字符 → 跳过
                if tail and tail[0] in _FORMULA_CHARS:
                    continue
                # 干净候选：记住最后一个干净值；优先返回最后干净候选
                clean_candidate = (float(val), m.start())
            if clean_candidate is not None:
                return clean_candidate[0]

        # 回退：如果有维度分数，取加权平均
        dims = self._extract_dimension_scores(critic_result, min_output_len=300)
        if dims:
            weights = {"innovation": 0.30, "feasibility": 0.25, "rigor": 0.25, "expression": 0.20}
            total = sum(dims.get(k, 0) * w for k, w in weights.items())
            return round(total, 4)
        return 0.0

    # 维度中英文映射
    _DIM_MAP = {
        "创新性": "innovation", "创新": "innovation", "innovation": "innovation",
        "可行性": "feasibility", "feasibility": "feasibility",
        "严谨性": "rigor", "rigor": "rigor",
        "表达质量": "expression", "expression": "expression", "表达": "expression",
        "完整性": "completeness", "completeness": "completeness",
        # v7.3.0: 方法手册 2 维口径（manual_2d）——就绪度维度
        "就绪度": "readiness", "readiness": "readiness",
    }
    # 各维度短板阈值（低于此值视为短板）
    # v6.8.3: 提升阈值，避免偏科通过（原 0.65/0.60 → 0.70/0.65）
    DIMENSION_FLOOR = {"innovation": 0.70, "feasibility": 0.70, "rigor": 0.70, "expression": 0.70, "completeness": 0.65, "readiness": 0.70}

    def _extract_dimension_scores(self, critic_result: Dict[str, Any],
                                  min_output_len: int = 0) -> Dict[str, float]:
        """从 critic 输出中提取 4 维度分数（P0-2）。

        兼容 v6.6.3 GLM-5.2 输出格式：
        - `| 创新性（innovation） | 0.05 |` （markdown 表格 + 括号别名）
        - `| 创新性（innovation） | 0.30 | 0.78 |` （markdown 表格含权重列，得分列在最后）
        - `创新性：0.85` / `创新性 0.85` / `创新性（innovation） 0.85`

        v6.8.9 修复：表格行若含权重列（如 `| 维度 | 权重 | 得分 |`），
        原实现的正则会误匹配到权重列（第一个数字）。现改为取表格行内
        最后一个数字作为得分列。

        v6.8.50: min_output_len 参数——实时 hermes 输出传 300（正常评审输出
        含维度表/问题清单，过短必是错误文本，解析出的是伪分数）；解析落盘
        的 critic 报告文件传 0（文件存在即真实评审发生过，且单元测试用
        短样本验证解析器，不应被误拦）。

        Returns:
            {innovation, feasibility, rigor, completeness}
        """
        output = critic_result.get("output", "")
        import re
        dims: Dict[str, float] = {}
        # v6.8.46→v6.8.50: 短输出防线（仅实时评审路径启用，见 docstring）
        if min_output_len > 0 and len(output.strip()) < min_output_len:
            return dims
        # 收集所有"维度名+分数"对（去重，每个维度只取第一个匹配）
        for cn_name, en_key in self._DIM_MAP.items():
            if en_key in dims:
                continue
            score = None
            # 模式1：markdown 表格行。兼容 `| 维度 | 得分 |` 与 `| 维度 | 权重 | 得分 |`，
            # 分数总在行内最后一个数字列，故取该行最后一个 0.x 数字。
            table_m = re.search(
                rf"\|\s*{cn_name}[（(]?{en_key}[）)]?\s*\|[^|\n]*(\|[^|\n]*)*\|",
                output, re.IGNORECASE,
            )
            if table_m:
                # v6.8.9 修复：取表格行内"最后一个独立纯数字单元格"作为得分列。
                # 批评报告维度表格式为 `| 维度 | 权重 | 得分 | 档位 | 主要短板 |`，
                # 档位/主要短板评语中可能含数字（如 "U/W ~ 0.5"、"已扣 ceiling 0.05"、
                # "17.4%"），若直接取行内最后一个 0.x 会误读到评语中的数字。
                # 得分列总是独立成格的纯数字，故取最后一个匹配 `0.xx` 的单元格。
                # v6.9.78 修复：critic 实测会把得分写成 `**0.70**`（bsv R1
                # references 报告 `| 严谨性（rigor） | 0.50 | **0.70** | ...`），
                # 粗体单元格过不了 fullmatch，误取前一列权重 0.50 当得分——
                # 0.78 被记成 0.5，诱发"连续3轮下降"误暂停与 writer 连锁误扣。
                # 先剥离 markdown 强调（** __ ` *）再判纯数字。
                cells = table_m.group(0).strip().split("|")

                def _cell_score(cell: str):
                    t = cell.strip()
                    for _mark in ("**", "__", "`", "*"):
                        t = t.replace(_mark, "")
                    t = t.strip()
                    return float(t) if re.fullmatch(r"0\.\d+", t) else None

                pure_nums = [
                    n for n in (_cell_score(c) for c in cells) if n is not None
                ]
                if pure_nums:
                    score = pure_nums[-1]
            # 模式2：行内格式（表格未命中时兜底）
            if score is None:
                for pat in [
                    rf"{cn_name}[（(]{en_key}[）)]\s*[：:|]?\s*(0\.\d+)",   # 创新性（innovation） 0.05
                    rf"{cn_name}[：:]\s*(0\.\d+)",                            # 创新性：0.05
                    rf"{cn_name}\s+(0\.\d+)",                                 # 创新性 0.05
                ]:
                    m = re.search(pat, output, re.IGNORECASE)
                    if m:
                        score = float(m.group(1))
                        break
            if score is not None:
                dims[en_key] = score
        return dims

    def _get_weakest_dimension(self, dims: Dict[str, float]) -> str:
        """找出最弱的维度（P0-2，供 writer 聚焦改进）。"""
        if not dims:
            return ""
        return min(dims, key=dims.get)

    def _recalculate_score(self, dim_scores: Dict[str, float], project_type: str) -> float:
        """v6.8.7: 根据维度分数和项目类型权重重新计算综合分。"""
        standards = load_json(self.standards_path, default={})
        types = standards.get("project_types", {})
        weights_map = types.get(project_type, {}).get("evaluation_focus", {})
        # 映射中文权重名到英文 key
        weight_mapping = {
            "创新性权重": "innovation", "可行性权重": "feasibility",
            "严谨性权重": "rigor", "表达质量权重": "expression",
            "系统性权重": "systematic", "战略意义权重": "strategic",
            "完整性权重": "completeness",
        }
        if not weights_map:
            # 默认面上权重
            weights_map = {"创新性权重": 0.30, "可行性权重": 0.25, "严谨性权重": 0.25, "表达质量权重": 0.20}

        total_weight = 0.0
        weighted_sum = 0.0
        for cn_weight_key, en_dim_key in weight_mapping.items():
            w = weights_map.get(cn_weight_key, 0)
            if w > 0 and en_dim_key in dim_scores:
                weighted_sum += dim_scores[en_dim_key] * w
                total_weight += w

        if total_weight > 0:
            return round(weighted_sum / total_weight, 4)
        # 回退：简单平均
        return round(sum(dim_scores.values()) / max(len(dim_scores), 1), 4)

    # 元叙述/表格行特征——这些行提到 [critical]/[high] 只是引用或纪律说明，
    # 不是问题条目本身（实测 R8 报告 28 条"issue"全是表格行与评分说明，
    # 全量注入下一轮 critic prompt 造成 6.4KB 垃圾 + 逐条核对负担）
    _ISSUE_NOISE_PAT = re.compile(
        r"^\s*(\||#|>|---|```)"             # 表格/标题/引用/代码块行
        r"|红线抑制校验|纪律：|强制.*区间|评分块|综合评分"
        r"|执行清单|对照.*通过|不通过.*\||锚点对比结论"
    )

    def _extract_issues(self, critic_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从 critic 输出中提取问题列表。

        v6.9.66 修复：原实现是"行内含 [sev] 标记即收"——报告中的 Markdown
        表格行、评分说明、交叉引用（如"见 [high] anti_ai #4"）全部被误收，
        且一行含多个标记时重复收集（内层循环不 break）。实测 R8 报告产出
        28 条表格行垃圾，经 open_critical_issues 全量注入下一轮 critic
        prompt（要求逐条核对），是 critic 超时恶化（24h 成功率 7%）的
        主因之一。修复：噪声行过滤 + 每行只收最高严重级 + 实质性要求。
        """
        output = critic_result.get("output", "")
        issues = []
        seen_lines = set()
        for line in output.split("\n"):
            stripped = line.strip()
            if len(stripped) < 20:
                continue  # 过短行无实质内容
            if self._ISSUE_NOISE_PAT.search(stripped):
                continue
            found = None
            for sev in ("critical", "high", "medium", "low"):
                if f"[{sev}]" in stripped or f"（{sev}）" in stripped:
                    found = sev
                    break  # 只收最高严重级
            if not found:
                continue
            # 去重：同内容行只收一次
            key = stripped[:80]
            if key in seen_lines:
                continue
            seen_lines.add(key)
            issues.append({"severity": found, "line": stripped[:200]})
        return issues


# ---------------------------------------------------------------------------
# v6.8.22: P0 跨轮持久化（断裂点3、1、2、4 的数据基础）
# ---------------------------------------------------------------------------

    def _update_open_critical_issues(
        self,
        proposal_id: str,
        new_issues: List[Dict[str, Any]],
        current_round: int,
        focus_section_key: str,
    ) -> List[Dict[str, Any]]:
        """更新 proposal 的 open_critical_issues 列表（跨轮 P0 记忆）。

        逻辑：
        1. 仅吸纳 critical/high 级问题（P0/P1 级），medium/low 不入库。
        2. 去重：同 section + 同 severity + 描述相似度>0.8 视为同一问题，只更新最新轮次。
        3. 已存在但本轮 critic 报告中未再出现的问题 → 尝试标记为已解决（round_resolved）。
        4. 超过 MAX_P0_TRACK_ROUNDS 轮仍未被复现也未标记解决的问题 → 降级为 stale（保留记录）。
        5. 返回更新后的 open_critical_issues 列表。
        """
        MAX_P0_TRACK_ROUNDS = 10
        prop_state = self._get_proposal_state(proposal_id)
        if prop_state is None:
            return []
        open_list = prop_state.get("open_critical_issues", [])
        if not isinstance(open_list, list):
            open_list = []

        # 本轮 critic 报告的 section 归属
        section_key = focus_section_key or "full_review"

        # 1) 收集本轮出现的 critical/high 问题签名
        current_sigs = set()
        current_entries = []
        for issue in (new_issues or []):
            sev = issue.get("severity", "").lower()
            if sev not in ("critical", "high"):
                continue  # 只跟踪 P0/P1 级
            desc = (issue.get("line") or issue.get("description") or "").strip()
            if not desc:
                continue
            sim_key = self._issue_similarity_key(desc)
            sig = (section_key, sev, sim_key)
            current_sigs.add(sig)
            current_entries.append({
                "severity": sev,
                "section": section_key,
                "description": desc[:300],
                "first_seen_round": current_round,
                "last_seen_round": current_round,
                "round_resolved": None,
                "stale": False,
            })

        # 2) 合并：保留历史 + 更新 last_seen / 标记解决
        seen_this_round = set()
        merged = []
        for entry in open_list:
            if not isinstance(entry, dict):
                continue
            sig = (entry.get("section", ""), (entry.get("severity") or "").lower(), self._issue_similarity_key(entry.get("description", "")))
            if sig in current_sigs:
                # v7.2.62: 复发追踪（自迭代环②快速路径）——曾被标记解决
                # 的问题再次出现 = writer「改一崩二」打地鼠签名（实测新增
                # 问题 54% 由修复动作引入）。逐条计数，供轮间升级通道
                # 直接注入 writer prompt（无需等连续两轮负 delta）。
                if entry.get("round_resolved") is not None:
                    entry["recurrence_count"] = int(entry.get("recurrence_count", 0) or 0) + 1
                # 本轮仍出现 → 更新 last_seen，清除 resolved（若曾被误标记）
                entry["last_seen_round"] = current_round
                entry["round_resolved"] = None
                entry["stale"] = False
                seen_this_round.add(sig)
            elif (
                entry.get("section") == section_key
                and entry.get("round_resolved") is None
                and not entry.get("stale")
            ):
                # v6.9.37 修复：仅当条目所属章节正是本轮评审章节且未复现时才标记解决。
                # 原实现不比较章节——一轮内后续章节的 critic 调用会把先前章节刚入库
                # 的 P0 全部误标"已解决"（每轮含 3 个章节 critic + full_review +
                # references 共 5 次调用，current_sigs 只含本章节问题签名，其余
                # 章节条目一律落入"未复现→已解决"分支）。运行时实证：6 个课题全部
                # 条目 round_resolved == first_seen_round（同轮入库同轮被杀，
                # 08-22 16h 健康检查），跨轮 P0 记忆实际只存活到下一个 critic job，
                # writer 跨章节修复与 completion 的 P0 清零检查因此系统性失真。
                entry["round_resolved"] = current_round
            merged.append(entry)

        # 3) 加入本轮新出现、且历史不存在的问题
        for entry in current_entries:
            sig = (entry["section"], entry["severity"], self._issue_similarity_key(entry["description"]))
            if sig not in seen_this_round:
                merged.append(entry)
                seen_this_round.add(sig)

        # 4) 超长滞留未复现且已标记解决的，超过 MAX_P0_TRACK_ROUNDS 轮未复现 → stale 降级
        for entry in merged:
            if entry.get("stale"):
                continue
            resolved = entry.get("round_resolved")
            if resolved is not None and (current_round - resolved) > MAX_P0_TRACK_ROUNDS:
                entry["stale"] = True

        # 5) 列表上限保护（最近 40 条，critical 优先 + last_seen_round 降序保留）。
        # v7.2.56（#6 偏离修复，v6.10.2 候选优化合并）：旧排序只按 last_seen——
        # 存量达 40 上限时 critical 条目会被新近的 high 挤出存储，跨轮 P0
        # 记忆静默丢失（实测 4 课题有效 critical 14-20 条）。critical 优先
        # 排序保证上限裁剪只作用于 non-critical。
        merged.sort(key=lambda e: (
            0 if (e.get("severity") or "").lower() == "critical" else 1,
            -(e.get("last_seen_round", 0) or 0)))
        merged = merged[:40]

        prop_state["open_critical_issues"] = merged
        self._set_proposal_state(proposal_id, prop_state)
        return merged

    def _issue_similarity_key(self, description: str) -> str:
        """生成问题描述的可比对相似键：取前 30 个字符，去掉空白与标点，小写。

        用于跨轮去重——同一问题在不同轮次的措辞略有差异时仍能识别为同一问题。
        """
        import re
        if not description:
            return ""
        norm = re.sub(r"[\s，。；：、,.!?！？;:'\"“”‘’（）()\[\]【】\-—]", "", description.lower())
        return norm[:30]

    def _load_open_critical_issues(self, proposal_id: str) -> List[Dict[str, Any]]:
        """读取指定 proposal 的 open_critical_issues 列表（供 prompt 注入）。"""
        prop_state = self._get_proposal_state(proposal_id)
        if prop_state is None:
            return []
        open_list = prop_state.get("open_critical_issues", [])
        return [e for e in (open_list or []) if isinstance(e, dict)]

    def _build_p0_memory_text(self, proposal_id: str, exclude_resolved: bool = True) -> str:
        """构建注入 critic/writer prompt 的历史 P0 记忆文本。

        exclude_resolved=True（critic 用）：只列出仍未解决（round_resolved is None）的 P0。
        exclude_resolved=False（writer 用）：列出全部未解决 + 最近已解决的问题。

        v7.2.62: 未解决列表排序加入复发计数优先——复发问题（曾解决
        后又被复见）排在同 severity 首位，避免被截断挤出注入。
        """
        entries = self._load_open_critical_issues(proposal_id)
        if not entries:
            return ""

        def _is_noise(e):
            """表格行/元叙述噪声过滤（v6.9.66）——历史存量含大量误收条目。"""
            d = str(e.get("description", ""))
            return bool(re.match(r"^\s*(\||#|>|---|```)", d)) or \
                bool(re.search("红线抑制校验|纪律：|综合评分|执行清单|锚点对比结论", d))

        unresolved = [e for e in entries
                      if e.get("round_resolved") is None and not e.get("stale") and not _is_noise(e)]
        # v7.2.56（#6 偏离修复，v6.10.2 候选优化合并）：注入上限从平顶 [:12]
        # 改为「critical 子集下限保护 + non-critical 动态截断」——
        # ① critical 全量注入不设上限（实测 4 课题有效 critical 14-20 条，
        #   平顶截断把 2-8 条 P0 挤出注入，修复信号静默丢失）；
        # ② non-critical 截断 12 - critical 条数（注入总量维持 ~12 条聚焦
        #   水位，P0 记忆是聚焦信号不是全量账本，历史全量注入实测 6.4KB
        #   噪声稀释 critic 注意力）。
        unresolved.sort(key=lambda e: (
            0 if (e.get("severity") or "").lower() == "critical" else 1,
            -int(e.get("recurrence_count", 0) or 0),
            -(e.get("last_seen_round", 0) or 0)))
        crit_n = sum(
            1 for e in unresolved
            if (e.get("severity") or "").lower() == "critical")
        non_crit = [e for e in unresolved
                    if (e.get("severity") or "").lower() != "critical"]
        unresolved = [e for e in unresolved
                      if (e.get("severity") or "").lower() == "critical"] + \
            non_crit[:max(0, 12 - crit_n)]
        if exclude_resolved:
            target = unresolved
        else:
            # writer 需要看到未解决 + 最近 3 条已解决（防止反复横跳）
            resolved = sorted(
                [e for e in entries if e.get("round_resolved") is not None and not _is_noise(e)],
                key=lambda e: e.get("round_resolved", 0), reverse=True,
            )[:3]
            target = unresolved + resolved

        if not target:
            return ""

        sev_cn = {"critical": "严重(P0)", "high": "较高(P1)"}
        lines = []
        for e in target:
            sev = (e.get("severity") or "high").lower()
            if e.get("round_resolved") is None:
                status = f"待解决（首见于 R{e.get('first_seen_round')}）"
            else:
                status = f"已解决（R{e.get('round_resolved')} 起未复现）"
            lines.append(
                f"- [{sev_cn.get(sev, sev)}] 归属章节={e.get('section','?')} 状态={status} "
                f"问题：{e.get('description','')[:120]}"
            )
        block = "\n".join(lines)
        return (
            f"\n\n【历史遗留问题记忆（跨轮持久化，必须逐条核对）】\n"
            f"以下问题是此前多轮对抗评审中反复/遗留的 P0 级问题，请务必处理：\n"
            f"{block}\n"
        )

    def _build_recurrence_escalation_text(self, proposal_id: str) -> str:
        """v7.2.62: 复发问题升级块（自迭代环②快速路径）。

        从问题账本筛出 recurrence_count ≥ 1 且当前未解决/未陈化的条目
        ——「曾被 critic 标记解决、后续轮次又复现」即 writer 修复动作
        引入新伤的打地鼠签名（全库实证：新增问题 54% 属此类）。

        与旧顽固升级块（_build_writer_escalation_block，需连续两轮
        monitor 负 delta，周级延迟）互补：本通道由账本直接驱动，
        每个轮次边界自动生效（轮级延迟），是大模型节拍的自迭代通道。

        零 LLM：纯账本读取 + 文本拼装。
        """
        try:
            entries = self._load_open_critical_issues(proposal_id) or []
        except Exception:
            return ""
        recurred = [
            e for e in entries
            if isinstance(e, dict)
            and int(e.get("recurrence_count", 0) or 0) >= 1
            and e.get("round_resolved") is None
            and not e.get("stale")
        ]
        if not recurred:
            return ""
        recurred.sort(key=lambda e: (-int(e.get("recurrence_count", 0) or 0),
                                     0 if (e.get("severity") or "").lower() == "critical" else 1))
        recurred = recurred[:8]
        lines = []
        for e in recurred:
            sev = (e.get("severity") or "high").lower()
            lines.append(
                f"- [{sev}] 章节={e.get('section', '?')} "
                f"复发 {int(e.get('recurrence_count', 0) or 0)} 次："
                f"{str(e.get('description', ''))[:120]}"
            )
        block = "\n".join(lines)
        return (
            f"\n\n【复发问题升级令（打地鼠拦截，最高优先级）】\n"
            f"以下问题曾在本课题被标记\"已解决\"后又重新出现——这是修复动作"
            f"本身引入新伤的签名（改一崩二）。本轮禁止再走\"局部补丁\"路线：\n"
            f"{block}\n"
            f"执行要求：\n"
            f"  1. 对每条复发问题，先定位上一轮修复动作本身错在哪里（而非表面症状）\n"
            f"  2. 修复必须覆盖全部受影响位置（全稿 grep 同型表述），不得只改聚焦段\n"
            f"  3. 输出「问题→根因→修复位置清单」对照表，供下轮 critic 逐项核销\n"
        )

    def _build_evidence_protocol_block(
        self,
        proposal_id: str,
        prop_dir: Optional[Path],
        section_key: str,
    ) -> str:
        """v7.2.67: PaperQA2 式证据协议块（写作前置纪律注入，零 LLM）。

        对标 PaperQA2「Paper Search → Gather Evidence → Generate Answer」
        三段式——每个论断强制挂检索证据的引用。本系统素材断链实证：
        kb-methods-pack 从不进 writer prompt、2200+ 页知识库对 writer
        只以 3 页 ×400 字 digest 入场、gap=0 短路后 writer 零新文献。
        本块把「检索-取证-挂引用」变成写作前置纪律，补生成端源头
        （enforcement 既有：critic references 轮三池红线 + params 口径校验）。

        证据池探测（存在的才列，路径相对课题目录）：
          - 02_literature/targeted-research/lit-gap-*.md（mtime 最新 1 份）
          - 02_literature/reading-notes.md
          - 02_literature/candidates.bib（或 candidates-*.bib；实际布局中
            多源检索 BibTeX 副产物落在 targeted-research/ 下，一并回退探测）
          - 03_method/kb-methods-pack.md
          - 03_method/method-manual.md
          - 04_proposal/params.json

        章节适配：
          - rationale/content → 空串（该两轮以论证结构为主，避免 prompt 膨胀）
          - scheme → 完整四条纪律 + 方法参数溯源附加要求
          - references → 完整四条纪律 + 逐字段对照三池誊写附加要求
          - full_review → 精简版（仅前两条纪律，控骨架轮 prompt 体量）
          - 证据池全空 → 精简协议（禁新增无出处论断），不抛异常

        零 LLM：纯文件系统探测 + 文本拼装；任何异常 fail-open 返回空串。
        """
        try:
            # 章节适配第一道闸：论证结构为主的章节不注入（避免 prompt 膨胀）
            if section_key in ("rationale", "content"):
                return ""

            if prop_dir is None:
                prop_dir = self._find_proposal_dir(proposal_id)
            if prop_dir is None or not Path(prop_dir).exists():
                prop_dir = None

            def _mtime(p: Path) -> float:
                try:
                    return p.stat().st_mtime
                except OSError:
                    return 0.0

            # 证据池清单：按固定优先级探测，存在的才列
            sources: List[str] = []
            if prop_dir is not None:
                lit_root = prop_dir / "02_literature"
                lit_dir = lit_root / "targeted-research"
                # 1) 最新定向检索报告（lit-gap-*.md，取 mtime 最新 1 份）
                try:
                    lit_gaps = sorted(
                        lit_dir.glob("lit-gap-*.md"),
                        key=_mtime, reverse=True,
                    )
                except OSError:
                    lit_gaps = []
                if lit_gaps:
                    try:
                        sources.append(str(lit_gaps[0].relative_to(prop_dir)))
                    except ValueError:
                        sources.append(str(lit_gaps[0]))
                # 2) 已核实文献阅读笔记
                if (lit_root / "reading-notes.md").exists():
                    sources.append("02_literature/reading-notes.md")
                # 3) 候选文献 BibTeX：candidates.bib 精确名优先，
                #    回退 candidates-*.bib（02_literature/ 与 targeted-research/
                #    两处布局都探测，各取最新 1 份）
                bib_rel = ""
                if (lit_root / "candidates.bib").exists():
                    bib_rel = "02_literature/candidates.bib"
                else:
                    cands = sorted(
                        lit_root.glob("candidates-*.bib"),
                        key=_mtime, reverse=True,
                    )
                    if not cands:
                        cands = sorted(
                            lit_dir.glob("candidates-*.bib"),
                            key=_mtime, reverse=True,
                        )
                    if cands:
                        try:
                            bib_rel = str(cands[0].relative_to(prop_dir))
                        except ValueError:
                            bib_rel = str(cands[0])
                if bib_rel:
                    sources.append(bib_rel)
                # 4-6) 方法卡素材包 / 方法学手册 / 数值口径表
                for rel in (
                    "03_method/kb-methods-pack.md",
                    "03_method/method-manual.md",
                    "04_proposal/params.json",
                ):
                    if (prop_dir / rel).exists():
                        sources.append(rel)

            # 证据池说明表（按路径尾部匹配，供清单行展示）
            _desc_rules = (
                ("lit-gap-", "定向检索报告（最新一份）"),
                ("reading-notes.md", "已核实文献阅读笔记"),
                ("candidates", "候选文献标准 BibTeX 条目"),
                ("kb-methods-pack.md", "知识库方法卡素材包"),
                ("method-manual.md", "课题方法学手册（单一真相源）"),
                ("params.json", "数值/机制口径表（canonical）"),
            )

            def _desc(rel: str) -> str:
                for key, text in _desc_rules:
                    if key in rel:
                        return text
                return "证据源"

            # 证据池全空：精简协议（禁新增无出处论断），不崩
            if not sources:
                return (
                    "\n\n【证据池协议（精简版：当前课题证据池为空，v7.2.67）】\n"
                    "未检出任何证据池文件（定向检索报告/阅读笔记/BibTeX/"
                    "方法卡素材包/方法学手册/口径表）。本轮纪律：\n"
                    "  ① 不得新增无出处支撑的数值/机制表述/方法参数/文献条目；\n"
                    "  ② 确属方案设定且暂无文献出处的论断，明确标注"
                    "「方案设定值（待标定）」，\n"
                    "     不得凭记忆转录文献内容（杜撰红线）。\n"
                )

            pool_lines = "\n".join(
                f"  {i}. {rel} —— {_desc(rel)}"
                for i, rel in enumerate(sources, 1)
            )

            if section_key == "full_review":
                # full_review 精简版：只给前两条纪律（控骨架轮 prompt 体量）
                return (
                    "\n\n【证据池协议（PaperQA2 式写作前置纪律·精简版，v7.2.67）】\n"
                    f"课题目录：{prop_dir}\n"
                    "证据池清单（已确认存在，路径相对课题目录）：\n"
                    f"{pool_lines}\n"
                    "核心纪律：\n"
                    "  ① 写作前必须逐一读取上列存在的证据源；读不到的不得凭印象引用。\n"
                    "  ② 每个新增数值/机制表述/方法参数必须挂 [N] 引用，且该条目"
                    "须在证据池中有出处记录；\n"
                    "     池中无出处的论断要么删除，要么明确标注"
                    "「方案设定值（待标定）」。\n"
                )

            # scheme / references / 其余轮：完整四条纪律 + 轮次附加要求
            if section_key == "scheme":
                extra = (
                    "本轮为 scheme 轮附加要求（方法参数溯源）：研究方案涉及的"
                    "激光参数（波长/脉宽/光强）、材料参数（厚度/带隙/载流子"
                    "密度）、数值模拟设置（网格/边界/收敛判据）等，必须逐一"
                    "溯源到证据池（方法卡素材包/方法学手册/检索报告）中的"
                    "出处记录，无出处的按纪律②处理。\n"
                )
            elif section_key == "references":
                extra = (
                    "本轮为 references 轮附加要求（逐字段对照三池誊写）：每条"
                    "文献条目（作者链/标题/期刊/卷期页/DOI/arXiv ID）必须"
                    "逐字段对照证据池中的 lit-gap 检索结果、candidates "
                    "BibTeX、reading-notes 三池真实记录誊写；池中无对应记录"
                    "的条目一律不得写入（宁可少一条，不可编一条）。\n"
                )
            else:
                extra = ""
                # v7.3.3: KB wikilink 落地纪律（scheme 轮）——修复 v7.2.30
                # 守卫与 writer 的两侧脱节：守卫要求正文有 [[methods/...]]
                # 引用，writer 纪律却从未要求写该语法（全库 0/8 实测）。
                if section_key == "scheme":
                    extra = (
                        "  ⑤ KB 方法页引用落地：凡方法参数/实施细节取材自"
                        " kb-methods-pack.md 列出的方法页，须在正文相应位置"
                        "以 [[methods/<slug>]] 节点标注来源（整轮 ≥3 个、"
                        "slug 须与素材包中的 wikilink 一致）；取自论文方法"
                        "卡的用 [[papers/<slug>]]。这是知识库溯源闭环的"
                        "机器可校验形态，wikilink 守卫按此计数。\n"
                    )

            return (
                "\n\n【证据池协议（PaperQA2 式写作前置纪律，v7.2.67）】\n"
                f"课题目录：{prop_dir}\n"
                "证据池清单（已确认存在，路径相对课题目录，动笔前逐一读取）：\n"
                f"{pool_lines}\n"
                "核心纪律（违反按 rigor 清单③文献支撑真实 critical 计）：\n"
                "  ① 写作前必须逐一读取上列存在的证据源；读不到的不得凭印象引用。\n"
                "  ② 每个新增数值/机制表述/方法参数必须挂 [N] 引用，且该条目"
                "须在证据池中有出处记录；\n"
                "     池中无出处的论断要么删除，要么明确标注"
                "「方案设定值（待标定）」。\n"
                "  ③ 不得从记忆转录文献内容（作者链/标题/期刊/卷期页/DOI/"
                "参数/结论）——杜撰红线。\n"
                "  ④ 与 params.json 口径表冲突的表述以 canonical 条目为准，"
                "不得另立口径。\n"
                f"{extra}"
            )
        except Exception:
            # fail-open：协议块是纪律增强，任何异常不应阻断 writer 派活
            return ""


# ---------------------------------------------------------------------------
# v6.9.42: references 程序化预检（编号一致性正则比对 + 膨胀检测）
# ---------------------------------------------------------------------------

def _references_preflight(prop_dir: Path) -> str:
    """references 评审的程序化预检（零 LLM）。

    完成旧 prompt 交给 critic 的"编号一致性"检查：
    - 正文 [N] 引用标记全集（rationale/content/scheme 三章节）
    - 文献列表编号全集（兼容 `**[N]**` 粗体与 `[N]` 行首两种体例）
    - 两者比对：正文引用但列表缺失 / 列表存在但正文未引用 / 编号连续性
    - 总数对标 20-40 篇区间
    - 膨胀告警：references.md > 25KB 提示工作日志污染（35 条文献正常
      约 8-12KB，超出部分大概率是 §D-F 核校日志，应迁 05_review）

    Returns:
        预检报告文本（几 KB，直接附入 critic prompt）。
    """
    import re

    sections_dir = prop_dir / "04_proposal" / "sections"
    lines = []

    # ① 正文引用标记
    body_cites: set = set()
    per_section = {}
    for sec in ("rationale", "content", "scheme"):
        p = sections_dir / f"{sec}.md"
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        # [N] 角标；排除 [critical]–[medium] 类英文标签（只取纯数字）
        marks = set(int(m) for m in re.findall(r"\[(\d{1,3})\]", text))
        per_section[sec] = sorted(marks)
        body_cites.update(marks)

    # ② 文献列表编号（粗体 **[N]** 或行首 [N]）
    ref_path = sections_dir / "references.md"
    ref_ids: set = set()
    ref_size = 0
    ref_text = ""
    if ref_path.exists():
        ref_text = ref_path.read_text(encoding="utf-8")
        ref_size = len(ref_text.encode("utf-8"))
        # 粗体体例：**[1]** Author...（实测 bsv 等 writer 采用）
        ref_ids.update(int(m) for m in re.findall(r"\*\*\[(\d{1,3})\]\*\*", ref_text))
        # 行首体例：[1] Author...
        ref_ids.update(int(m) for m in re.findall(r"^\[(\d{1,3})\]", ref_text, re.M))

    missing = sorted(body_cites - ref_ids)
    uncited = sorted(ref_ids - body_cites)
    continuity = (
        "连续（1–%d 无缺口）" % max(ref_ids)
        if ref_ids and ref_ids == set(range(1, max(ref_ids) + 1))
        else f"不连续（缺口：{sorted(set(range(1, max(ref_ids)+1)) - ref_ids)[:10] if ref_ids else []}）"
        if ref_ids else "（列表为空或格式未识别）"
    )

    lines.append(f"- 正文引用标记：{len(body_cites)} 个不同编号")
    for sec, marks in per_section.items():
        if marks:
            lines.append(f"  - {sec}: {len(marks)} 个（{marks[0]}–{marks[-1]}）")
    lines.append(f"- 文献列表条目：{len(ref_ids)} 条（编号 {min(ref_ids) if ref_ids else '-'}–{max(ref_ids) if ref_ids else '-'}，{continuity}）")
    lines.append(f"- 正文引用但列表缺失：{missing if missing else '无'}")
    lines.append(f"- 列表存在但正文未引用：{uncited if uncited else '无'}")
    lines.append(f"- 引用数量对标：{'达标（20-40 篇）' if 20 <= len(ref_ids) <= 40 else f'超出区间（{len(ref_ids)} 篇）' if len(ref_ids) > 40 else f'低于区间（{len(ref_ids)} 篇，注意未编号的研读基础文献不算问题）'}")

    # ③ 膨胀告警
    if ref_size > 25 * 1024:
        lines.append(
            f"- ⚠ 膨胀告警：references.md 达 {ref_size // 1024}KB（{len(ref_ids)} 条文献正常约 "
            f"{max(8, len(ref_ids) // 4)}-{len(ref_ids) // 3}KB）。超出部分大概率是核校工作日志"
            f"（§D 映射表/§E 核实声明/§F 闭环证据），属 05_review 域内容——建议要求 writer "
            f"将工作日志迁出，仅保留文献条目与条目内挂钩注释。"
        )

    # ④ 来源校验（v6.9.57）：参考文献条目的 DOI/arXiv ID 必须能在课题
    # 检索产物（02_literature/，含 targeted-research / gap-analysis /
    # reading-notes 全部轮次）中找到——R7 实测 writer 凭记忆虚构元数据
    # （[4][11][13][26] 作者虚构 + [12][29] 卷期页错位），此前只能靠
    # critic 下游 CrossRef 核查救火，本预检把防线前移到评审输入。
    lines.extend(_reference_source_preflight(prop_dir, ref_text if ref_path.exists() else ""))

    return "\n".join(lines)


def _collect_reference_ids(text: str) -> set:
    """从文本中收集 DOI 与 arXiv ID（归一化小写、去尾部标点）。

    v6.9.59 修复：① DOI 排除集补全角标点（；，、）——实测条目形如
    "DOI: 10.1364/OPTICA.510789；arXiv:2302.04127" 时全角分号不在
    排除集，匹配吞成复合污染 ID 导致整条误报"虚构风险"（7 课题实测
    9 条）；② arXiv 分支允许尾部句点/逗号并统一 rstrip，与 DOI 分支
    对称（此前行尾 "arXiv:2302.04127." 整条漏提取）。
    """
    import re as _re
    ids = set()
    _tail = ".,;)】]”）)*`'\""
    ids.update(
        m.lower().rstrip(_tail)
        for m in _re.findall(r"10\.\d{4,5}/[^\s,;；，、）)\|]+", text)
    )
    ids.update(
        m.lower().rstrip(_tail)
        for m in _re.findall(r"(?<![\d.])\d{4}\.\d{4,5}(?!\d)", text)
    )
    return ids


def _reference_source_preflight(prop_dir: Path, ref_text: str) -> list:
    """来源校验段（零 LLM）：references 条目 ID vs 检索产物池。

    Returns:
        追加到预检报告的行列表。
    """
    import re as _re

    if not ref_text:
        return []

    # 可信池：课题检索产物（02_literature/ 全部轮次）+ 知识库论文页
    # frontmatter（researcher 经检索流水线入库，DOI/arxiv_id 可信）。
    # v6.9.57 实测：仅 02_literthesis 池漏掉大量经知识库/早期轮次来源
    # 的经典文献（27 条中 24 条误报），扩充后误报显著收敛。
    pool: set = set()
    lit_dir = prop_dir / "02_literature"
    if lit_dir.exists():
        for p in lit_dir.rglob("*"):
            if p.suffix.lower() in (".md", ".json") and p.is_file():
                try:
                    pool.update(_collect_reference_ids(
                        p.read_text(encoding="utf-8", errors="ignore")))
                except OSError:
                    continue

    papers_dir = _pl.PROJECT_ROOT / "knowledge" / "wiki" / "papers"
    if papers_dir.exists():
        for p in papers_dir.glob("*.md"):
            try:
                # v6.9.62（R1 降噪）：原 gate 要求 head 含 doi:/arxiv 字样，
                # 266/741 页被整页丢弃（其中不少页 frontmatter related 或
                # 文件名含可提取 ID）；另有 187 个 ID 因 2KB head 截断漏检
                # ——12h 健康检查实测 unmatched 误报率 20%-96%，公认经典
                # 文献（Goulielmakis 2010、Krausz RMP）被标"虚构风险"。
                # 两步降噪（不降低虚构检测灵敏度——只影响"有没有提取到"，
                # 不影响"提取到的 ID 是否可信"）：
                # ① 先读 head 2KB 提取（覆盖绝大多数 frontmatter，控 IO）；
                # ② head 提取为空 → 回退全文提取（消除截断漏检）。
                head = p.open(encoding="utf-8", errors="ignore").read(2048)
                ids = _collect_reference_ids(head)
                if not ids:
                    ids = _collect_reference_ids(
                        p.read_text(encoding="utf-8", errors="ignore"))
                pool.update(ids)
            except OSError:
                continue

    if not pool:
        return ["- 来源校验：检索产物池与知识库均为空，跳过"]

    out = []
    unmatched = []
    no_id = []
    ref_ids_hit = []
    for line in ref_text.splitlines():
        m = _re.match(r"^(?:\*\*)?\[(\d{1,3})\]?", line.strip())
        if not m:
            continue
        num = int(m.group(1))
        ids = _collect_reference_ids(line)
        if not ids:
            no_id.append(num)
            continue
        if ids & pool:
            ref_ids_hit.append(num)
        else:
            unmatched.append(num)

    if unmatched:
        out.append(
            f"- 来源校验：{len(unmatched)}/{len(ref_ids_hit + unmatched)} 条参考文献的 DOI/arXiv ID "
            f"未在本课题检索产物（02_literature/）与知识库中找到（编号 {unmatched[:15]}）——"
            f"这些条目属 writer 凭学科知识引用，元数据（作者/卷期页/DOI）未经检索验证，"
            f"是虚构风险集中区。请优先对这批做 CrossRef/DOI 核查；writer 后续轮次补充检索时"
            f"应将命中文献回录检索池（R7 实测教训：6 条凭记忆条目经 CrossRef 核查为虚构/错位，"
            f"致评分暴跌）。"
        )
    else:
        out.append(f"- 来源校验：全部条目 ID 均命中检索产物池/知识库（池 {len(pool)} 个标识符），元数据可信度高")
    if no_id:
        out.append(
            f"- ○ 无标识符条目 {len(no_id)} 条（编号 {no_id[:10]}）：无 DOI/arXiv ID 无法程序化"
            f"溯源，建议要求 writer 补齐标识符或说明来源（书籍/报告类可豁免）。"
        )
    return out


# ---------------------------------------------------------------------------
# v6.9.46: 跨章节指标一致性程序化预检（full_review critic 专用）
# ---------------------------------------------------------------------------

def _cross_section_metrics_preflight(prop_dir: Path) -> str:
    """提取各章节的量化指标并跨章节比对（零 LLM）。

    对应质量标准"指标红线 P0：同一指标在不同章节的数值与口径必须一致"——
    旧安排让 critic 通读 180KB 全文去找数字矛盾（超时大户），本函数正则
    提取带单位的关键指标量（强度/时间/能量/温度/尺寸/百分比），按数值+
    单位聚类，标出跨章节不一致项与全文唯一项。

    Returns:
        预检报告文本（直接附入 full_review critic prompt）。
    """
    import re

    # 指标型"数值+单位"模式（物理量纲，排除纯编号/年份/引用角标）
    patterns = [
        (r"(\d+(?:\.\d+)?)\s*TW/cm[²2]", "峰值强度 TW/cm²"),
        (r"(\d+(?:\.\d+)?)\s*GW/cm[²2]", "强度 GW/cm²"),
        (r"(\d+(?:\.\d+)?)\s*mJ/cm[²2]", "能量密度 mJ/cm²"),
        (r"(\d+(?:\.\d+)?)\s*(?:fs|飞秒)\b", "时间 fs"),
        (r"(\d+(?:\.\d+)?)\s*(?:ps|皮秒)\b", "时间 ps"),
        (r"(\d+(?:\.\d+)?)\s*(?:nm|纳米)\b", "波长/尺寸 nm"),
        (r"(\d+(?:\.\d+)?)\s*(?:μm|um|微米)\b", "波长/尺寸 μm"),
        (r"(\d+(?:\.\d+)?)\s*(?:meV|毫电子伏)\b", "能量 meV"),
        (r"(\d+(?:\.\d+)?)\s*(?:eV|电子伏)\b", "能量 eV"),
        (r"(\d+(?:\.\d+)?)\s*(?:K|开尔文)\b(?![a-zA-Z])", "温度 K"),
        (r"(\d+(?:\.\d+)?)\s*(?:层|atomic layers?)\b", "层数"),
        (r"(\d+(?:\.\d+)?)\s*%", "百分比"),
    ]

    sections_dir = prop_dir / "04_proposal" / "sections"
    per_section_values: dict = {}
    for sec in ("rationale", "content", "scheme", "full_review"):
        p = sections_dir / f"{sec}.md"
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        found = {}
        for pat, label in patterns:
            for m in re.finditer(pat, text):
                val = m.group(1)
                found.setdefault(label, set()).add(val)
        per_section_values[sec] = found

    lines = []
    # 跨章节不一致检测：同一量纲在不同章节出现但数值集不同
    all_labels = sorted({lbl for fv in per_section_values.values() for lbl in fv})
    issues = []
    consistent = []
    for label in all_labels:
        secs_with = {sec: fv[label] for sec, fv in per_section_values.items() if label in fv}
        if len(secs_with) < 2:
            continue
        union = set().union(*secs_with.values())
        # 章节间数值集完全一致 → 一致；存在差异 → 需人工判断（可能为区间/上限不同表述）
        if all(v == union for v in secs_with.values()) and len(union) == 1:
            consistent.append(f"{label}={next(iter(union))}")
        else:
            detail = "; ".join(f"{sec}:{sorted(v)}" for sec, v in secs_with.items())
            issues.append(f"  - {label}: {detail}")
    lines.append(f"- 跨章节完全一致的指标：{len(consistent)} 项"
                 + (f"（{', '.join(consistent[:8])}{'…' if len(consistent) > 8 else ''}）" if consistent else ""))
    if issues:
        lines.append(f"- ⚠ 数值集存在差异的指标（{len(issues)} 项，请核对是口径差异还是矛盾）：")
        lines.extend(issues[:10])
    else:
        lines.append("- 无数值集差异项")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# v6.10.0（T3）: 方法学专题参考注入（方法页反哺 writer/critic）
# ---------------------------------------------------------------------------

# 方法页目录与专区标记（与 weekend_pipeline/methods_jobs.py 同源约定；
# 此处不导入 weekend_pipeline——研究管线两个子包保持单向依赖
# weekend_pipeline → proposal_lifecycle，反向导入会成环）
_METHODS_WIKI_DIR_REL = "knowledge/wiki/methods"
_METHODS_LEXICON_REL = "memory/config/methods-lexicon.json"
_METHODS_INJECT_REL = "memory/config/methods-inject.json"
_SETTLE_BLOCK_BEGIN = "<!-- methods-settle:v1 -->"
_SETTLE_BLOCK_END = "<!-- /methods-settle:v1 -->"


def _methods_inject_settings() -> Dict[str, Any]:
    """读取注入开关配置（enabled/max_pages/max_chars；缺省默认开）。"""
    path = _pl.PROJECT_ROOT / _METHODS_INJECT_REL
    data = load_json(path, default={}) if path.exists() else {}
    try:
        return {
            "enabled": bool(data.get("enabled", True)),
            "max_pages": max(1, int(data.get("max_pages", 3) or 3)),
            "max_chars": max(120, int(data.get("max_chars", 400) or 400)),
        }
    except (TypeError, ValueError):
        return {"enabled": True, "max_pages": 3, "max_chars": 400}


def _extract_methods_digest(page_text: str, max_chars: int) -> str:
    """从方法页正文提取注入摘要：结构化专区（原理/参数表/代表作）优先，
    无专区时回退正文前 max_chars（剥离 frontmatter）。总长受 max_chars 截断。"""
    body = page_text
    if _SETTLE_BLOCK_BEGIN in page_text and _SETTLE_BLOCK_END in page_text:
        begin = page_text.index(_SETTLE_BLOCK_BEGIN) + len(_SETTLE_BLOCK_BEGIN)
        end = page_text.index(_SETTLE_BLOCK_END)
        body = page_text[begin:end]
    elif page_text.lstrip().startswith("---"):
        # 无专区的既有页：剥离 frontmatter，防止元数据块混入摘要
        from kb_text import parse_frontmatter as _pfm
        _, body = _pfm(page_text)
    keep: List[str] = []
    keep_section = False
    for line in body.split("\n"):
        stripped = line.strip()
        if stripped.startswith("## "):
            keep_section = any(
                stripped.startswith(f"## {k}")
                for k in ("原理", "参数表", "适用边界", "代表作")
            )
            if keep_section:
                keep.append(line)
            continue
        if keep_section and stripped and not stripped.startswith("- ["):
            keep.append(line)
    digest = "\n".join(keep).strip()
    if not digest:
        digest = body.strip()
    if len(digest) > max_chars:
        digest = digest[:max_chars] + "…"
    return digest


def _match_methods_pages(proposal_text: str, max_pages: int) -> List[Dict[str, str]]:
    """按课题关键词反向匹配方法页（词表 + 页面 frontmatter aliases）。

    Returns:
        [{"page": 文件名, "title": 标题, "digest": 摘要}]，命中词数
        降序取前 max_pages。
    """
    import re as _re
    if not proposal_text:
        return []
    text_n = _re.sub(r"[-–—]", " ", proposal_text.lower())

    # 词表别名 → 页文件名（手工编辑 lexicon 即时生效）
    lex_entries: List[Dict[str, Any]] = []
    lex_path = _pl.PROJECT_ROOT / _METHODS_LEXICON_REL
    if lex_path.exists():
        lex_entries = [
            e for e in (load_json(lex_path, default={}).get("entries") or [])
            if isinstance(e, dict) and e.get("page")
        ]

    def _hit(term: str) -> bool:
        term_n = _re.sub(r"[-–—]", " ", str(term).lower()).strip()
        if not term_n:
            return False
        if _re.search(r"[a-z]", term_n):
            if " " in term_n:
                return term_n in text_n
            return _re.search(rf"\b{_re.escape(term_n)}", text_n) is not None
        return term_n in text_n

    scored: Dict[str, Dict[str, Any]] = {}
    for entry in lex_entries:
        words = [entry.get("slug", "")] + list(entry.get("aliases", []) or []) \
            + list(entry.get("zh", []) or [])
        hits = sum(1 for w in words if w and _hit(w))
        if hits > 0:
            page = str(entry["page"])
            item = scored.setdefault(page, {"page": page, "hits": 0})
            item["hits"] += hits

    methods_dir = _pl.PROJECT_ROOT / _METHODS_WIKI_DIR_REL
    if not methods_dir.exists():
        return []
    from kb_text import parse_frontmatter as _pfm
    results: List[Dict[str, str]] = []
    for f in sorted(methods_dir.glob("*.md")):
        item = scored.get(f.name)
        if not item:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        fm, _body = _pfm(text)
        # frontmatter aliases 兜底匹配（词表未覆盖的既有页）
        if item["hits"] == 0:
            continue
        results.append({
            "page": f.name,
            "title": str(fm.get("title", f.stem)),
            "hits": item["hits"],
            "digest": _extract_methods_digest(text, 10 ** 6),  # 截断由调用方做
        })
    results.sort(key=lambda r: r["hits"], reverse=True)
    return results[:max_pages]


def _load_methods_reference_block(
    lifecycle_obj,
    proposal_id: str,
    prop_dir: Optional[Path] = None,
) -> str:
    """v6.10.0（T3）：方法页反哺 writer——按课题关键词匹配方法页，
    构造【方法学专题参考】块（原理+关键参数+代表作，页数/字数受
    methods-inject.json 控制，默认关 3 页 ×400 字）。

    匹配文本：课题 title（lifecycle state）+ 00 号研究设想前 2000 字。
    消费端：_run_writer_optimize 的 scheme 聚焦轮（研究内容与可行性
    论证的方法与参数依据）。开关关闭/无命中页返回空串。
    """
    try:
        settings = _methods_inject_settings()
        if not settings["enabled"]:
            return ""

        prop_state = lifecycle_obj._get_proposal_state(proposal_id) or {}
        match_text = str(prop_state.get("title", "") or "")
        if prop_dir is not None:
            for f in sorted(prop_dir.glob("00_*.md")):
                try:
                    match_text += "\n" + f.read_text(encoding="utf-8")[:2000]
                except Exception:
                    pass
                break
        if not match_text.strip():
            return ""

        pages = _match_methods_pages(match_text, settings["max_pages"])
        if not pages:
            return ""

        lines = [
            "\n\n【方法学专题参考（已验证方法知识页，v6.10.0）】",
            "以下方法页来自知识库方法学专题（含参数表与文献出处），",
            "研究内容与可行性论证可直接引用这些已验证方法与参数，",
            "引用时标注来源文献：",
            "",
        ]
        for p in pages:
            digest = p["digest"]
            if len(digest) > settings["max_chars"]:
                digest = digest[: settings["max_chars"]] + "…"
            lines.append(f"■ {p['title']}（{p['page']}）")
            lines.append(digest)
            lines.append("")
        if _log:
            _log.info(
                f"[{proposal_id}] 方法学参考注入: {len(pages)} 页 "
                f"({', '.join(p['page'] for p in pages)})"
            )
        return "\n".join(lines)
    except Exception as e:
        if _log:
            _log.warning(f"方法学参考注入失败（{proposal_id}，跳过）: {e}")
        return ""


def _methods_critic_hint() -> str:
    """v6.10.0（T3）：critic 的方法页核对提示（一行，不注入全文）。"""
    return (
        "\n【方法学参考核对】知识库维护有已验证方法页"
        f"（{_METHODS_WIKI_DIR_REL}/，含参数表与出处），"
        "申请书涉及方法参数/数值时可比对核验，不一致请在问题清单标注。\n"
    )


# ---------------------------------------------------------------------------
# v6.8.17: cross-proposal 范例注入
# ---------------------------------------------------------------------------

def _load_cross_proposal_exemplar(lifecycle_obj, current_proposal_id: str, section_key: str) -> str:
    """从最高分课题中提取范例段落，注入到低分课题的 writer prompt。

    v6.8.24 修复：旧版用 last_score + 阈值 0.80 → 所有课题从未达到 → 死代码。
    改为：用历史峰值分数（score_history 中的最大值），阈值降至 0.70，
    扫描 optimizing/ 和 pending_review/ 目录。

    v6.8.25 修复：旧版扫描各课题目录下的独立 _lifecycle.json，但实际所有状态
    存储在全局 research_proposals/_lifecycle.json 中，各课题目录无此文件 →
    函数永远跳过所有课题 → 完全失效。改为从全局状态文件读取。
    """
    try:
        from proposal_lifecycle.constants import PROPOSALS_ROOT

        # 找到当前课题的分数
        current_state = lifecycle_obj._get_proposal_state(current_proposal_id)
        current_score = current_state.get("last_score", 0.0) if current_state else 0.0
        if current_score >= 0.75:
            return ""  # 当前课题已足够好，不需要范例

        # v6.8.24: 从 score_history 取历史峰值，而非 last_score
        def _best_score_from_state(state: dict) -> float:
            """从 proposal state 中提取历史最高分。"""
            last = state.get("last_score", 0.0)
            history = state.get("score_history", [])
            if not history:
                return last
            peak = max((h.get("score", 0) for h in history if isinstance(h, dict)), default=0)
            return max(last, peak)

        # v6.8.25: 从全局 _lifecycle.json 读取所有课题状态，而非各课题目录下的独立文件
        global_state = lifecycle_obj._load_state()
        all_proposals = global_state.get("proposals", {})

        best_proposal = None
        best_score = 0.70  # v6.8.24: 门槛从 0.80 降至 0.70（实际可达到的水平）
        best_status = None
        for pid, pstate in all_proposals.items():
            if pid == current_proposal_id:
                continue
            # v6.8.25: 只从 optimizing 和 pending_review 状态的课题中选范例
            p_status = pstate.get("status", "")
            if p_status not in ("optimizing", "pending_review"):
                continue
            score = _best_score_from_state(pstate)
            if score > best_score:
                best_score = score
                best_proposal = pid
                best_status = p_status

        if not best_proposal or not best_status:
            return ""

        # 提取范例课题的对应章节
        section_file_map = {
            "rationale": "rationale.md",
            "content": "content.md",
            "scheme": "scheme.md",
        }
        section_file = section_file_map.get(section_key)
        if not section_file:
            return ""

        exemplar_path = PROPOSALS_ROOT / best_status / best_proposal / "04_proposal" / "sections" / section_file
        if not exemplar_path.exists():
            return ""

        text = exemplar_path.read_text(encoding="utf-8")
        # 取前 2000 字符作为范例（足够展示写作风格，不会太长）
        exemplar_text = text[:2000]

        # v6.9.3: 注入成功时留痕——此前函数无任何日志输出，2026-08-13/08-15
        # 两轮体检均因日志 0 条"参考范文"记录无法区分"已注入"与"从未触发"，
        # 被标记"潜在死代码风险"。一条 INFO 即可闭环观测。
        if _log:
            _log.info(
                f"[{current_proposal_id}] 范例注入: {section_key} ← {best_proposal} "
                f"(范文峰值分 {best_score:.2f}, 当前分 {current_score:.2f})"
            )

        return (
            f"\n\n【参考范文（来自评分 {best_score:.2f} 的高质量课题，仅供学习写作风格和论证密度）】\n"
            f"来源课题：{best_proposal}\n"
            f"章节：{section_file}\n"
            f"---\n{exemplar_text}\n---\n"
            f"请在本次修改中参考上述范文的论证密度、行文连贯性和具体性，"
            f"但不要照抄内容（研究领域不同）。\n"
        )
    except Exception:
        return ""
