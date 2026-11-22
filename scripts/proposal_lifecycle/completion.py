from __future__ import annotations

from typing import Any, Dict

from common import now_utc

from proposal_lifecycle.constants import (
    _log,
    DEFAULT_MAX_ROUNDS,
    DEFAULT_NO_IMPROVEMENT_LIMIT,
    DEFAULT_SCORE_THRESHOLD,
)

from proposal_sections import SECTION_KEYS, REVIEW_SECTION_KEYS


class CompletionMixin:
    # ------------------------------------------------------------------
    # 达标判定
    # ------------------------------------------------------------------

    # v6.8.0: 5 个申请书模块（含整体审查）全部通过才算达标
    # v7.3.0: 升级为 6 评审模块——新增 method_manual（方法手册开工就绪度），
    # 手册未过线（L<3 或 2 维分 <0.85 或有 critical/high 缺口）不算达标。
    # 用户裁决（2026-11-02）：手册的详细程度与完整度决定课题能否正式开工。
    REQUIRED_SECTIONS = REVIEW_SECTION_KEYS

    # v6.10.3 F1: 口径说明——references 步骤是 2 维专用口径（rigor/
    # completeness），且每轮步骤序固定 references 收尾，导致顶层
    # last_score 系统性等于 references 单模块分（实测 9 课题中 7 个
    # 末条 focus=references）。逃生阀晋级的质量警告此前用 last_score
    # 与达标线比较，references 高分（如 attosecond 0.85）会豁免警告，
    # 造成"1/5 模块通过却以无警告达标观感进队"的误读。
    @staticmethod
    def _last_section_score(prop_state: Dict[str, Any]) -> float:
        """取最近一条非 references/manual（4 维章节口径）的历史分。

        v7.3.0: method_manual 同为 2 维异口径（readiness/rigor），与
        references 一样排除出章节有效分序列。
        """
        for h in reversed(prop_state.get("score_history") or []):
            if h.get("focus_section") not in ("references", "method_manual"):
                try:
                    return float(h.get("score", 0.0))
                except (TypeError, ValueError):
                    continue
        return 0.0

    def _effective_score(self, prop_state: Dict[str, Any], monitor_score: float) -> Dict[str, Any]:
        """v6.10.3 F1: 计算整篇有效分（用于逃生阀质量警告口径）。

        优先级：monitor 独立整篇分 > 最近 4 维章节分 > last_score 兜底。
        返回 {score, caliber}，caliber 用于警告文本标注口径来源。
        """
        if monitor_score and monitor_score > 0:
            return {"score": monitor_score, "caliber": "monitor独立评分"}
        section_score = self._last_section_score(prop_state)
        if section_score > 0:
            return {"score": section_score, "caliber": "4维章节口径"}
        last = float(prop_state.get("last_score", 0.0) or 0.0)
        return {"score": last, "caliber": "last_score"}

    def _check_done(self, proposal_id: str, threshold: Dict[str, Any]) -> Dict[str, Any]:
        """判定 proposal 是否达到输出标准（P1-3: 所有模块对抗胜利才算达标）。

        达标条件：
        1. 条件1（达标）：5 个章节全部通过（分数达标 + 各维度无短板）
        2. 条件2（逃生阀）：连续N轮无显著提升
        3. 条件3（逃生阀）：达到最大轮数

        逃生阀触发时，如果分数低于达标线，附加 quality_warning 标记。
        """
        prop_state = self._get_proposal_state(proposal_id)
        if not prop_state:
            return {"done": False, "reason": "状态不存在"}

        # v7.3.42 用户裁决：A 通道从"5 模块全高自动晋级"改为析取提醒——
        # 任一模块判定分 ≥0.85 且该册无未解决 critical/high，即写一条
        # "建议专家评审"到人工队列。不晋级、不改 lifecycle 状态、不拦 B 通道。
        # 独立于 threshold（固定 0.85），关闭开关 LINSAI_A_GATE_PANEL_PROMPT=0
        # 则完全不判定、不写状态（零副作用）。
        from proposal_lifecycle.a_gate import (
            evaluate_panel_prompt,
            panel_prompt_enabled,
        )
        _panel_enabled = panel_prompt_enabled()
        if _panel_enabled:
            _panel = evaluate_panel_prompt(
                prop_state, self.REQUIRED_SECTIONS, proposal_id=proposal_id)
            if _panel:
                _prev = prop_state.get("a_gate_panel_request") or {}
                _same = (
                    _prev.get("module") == _panel["module"]
                    and _prev.get("round") == _panel["round"]
                    and abs(float(_prev.get("score") or 0.0) - _panel["score"]) < 0.005
                )
                if not _same:
                    _panel["proposal_id"] = proposal_id
                    _panel["created_at"] = now_utc()
                    prop_state["a_gate_panel_request"] = _panel
                    self._set_proposal_state(proposal_id, prop_state)
            elif prop_state.get("a_gate_panel_request"):
                # v7.3.65: 提醒存活条件复核——后续评审若已不满足（模块判定分
                # 回落 <0.85，或出现未解决 critical/high），撤回陈旧提醒，
                # 否则人工队列会一直指向已被新报告推翻的旧分。
                prop_state["a_gate_panel_request"] = None
                prop_state["updated_at"] = now_utc()
                self._set_proposal_state(proposal_id, prop_state)

        last_score = prop_state.get("last_score", 0.0)
        score_history = prop_state.get("score_history", [])
        # v6.9.78: references 轮是 2 维专用口径（rigor/completeness 均值，
        # 不含锚点绑定与 AI 天花板 cap），与章节 4 维加权分不可比——混入
        # 连续性窗口会制造虚假下降/平台/无提升信号（实测 bsv pass4：
        # 0.75→0.67→0.66→0.50[refs] 被误判"连续3轮质量下降"暂停流转，
        # 其中 0.50 还是解析缺陷所致，真实分为 0.78）。与 v6.9.62 的
        # dims_partial 防线同构：异口径条目不参与连续性判定。
        # v7.3.0: method_manual 轮同为 2 维专用口径（readiness/rigor 均值），
        # 与 references 同理排除出连续性判定。
        score_history = [
            h for h in score_history
            if h.get("focus_section") not in ("references", "method_manual")
        ]
        section_passes = prop_state.get("section_passes", {})  # P1-3
        min_score = threshold.get("min_overall_score", DEFAULT_SCORE_THRESHOLD)
        rounds = prop_state.get("optimization_rounds", 0)
        # v6.9.92: per-proposal 轮次上限覆盖。人工退回（reject+专项修复）
        # 后课题轮次已等于/超过 DEFAULT_MAX_ROUNDS，若不加宽，下一轮完成度
        # 检测立即再触发"达到最大轮数"逃生阀空转晋级（09-05 order-param
        # 退回场景：r8 上限 + 引用专项需 r9+ 空间）。覆盖字段为
        # max_rounds_override（正整数，缺省回落全局默认）。
        try:
            _ovr = int(prop_state.get("max_rounds_override") or 0)
        except (TypeError, ValueError):
            _ovr = 0
        max_rounds = _ovr if _ovr > 0 else DEFAULT_MAX_ROUNDS

        # v6.8.3: 获取 monitor 独立评分作为校准参考
        monitor_history = prop_state.get("monitor_history", [])
        monitor_score = 0.0
        if monitor_history:
            last_monitor = monitor_history[-1]
            monitor_score = last_monitor.get("monitor_independent_score", 0.0)

        # 条件1（P1-3）：所有模块对抗胜利 + monitor 复核通过
        # v7.3.41: A 通道判定改用 cap 前原始四维加权分（开关默认 on）。
        # 开关关闭时完全回退旧行为（只看 optimize 轮落盘的 section_passes）。
        from proposal_lifecycle.a_gate import module_gate_score, raw_gate_enabled
        if raw_gate_enabled():
            _floor = getattr(self, "DIMENSION_FLOOR", {})
            _raw_hist = prop_state.get("score_history", []) or []
            passed_sections = []
            for _s in self.REQUIRED_SECTIONS:
                _mg = module_gate_score(_raw_hist, _s)
                if not _mg["found"]:
                    # 无历史记录时回落 optimize 落盘的布尔结果（兼容旧数据
                    # 与测试夹具，不因缺 history 误判未通过）
                    if section_passes.get(_s):
                        passed_sections.append(_s)
                    continue
                if _mg["gate"] < min_score:
                    continue
                _weak = [
                    k for k, _f in _floor.items()
                    if k in (_mg["dim_scores"] or {}) and _mg["dim_scores"][k] < _f
                ]
                if not _weak:
                    passed_sections.append(_s)
        else:
            passed_sections = [s for s in self.REQUIRED_SECTIONS if section_passes.get(s)]
        all_passed = len(passed_sections) == len(self.REQUIRED_SECTIONS)
        if all_passed:
            # v6.8.9: monitor 作为第三方监管者把关——即使 writer-critic 对抗全部胜利，
            # 若 monitor 独立评分低于达标线，视为未达标，继续优化。
            # 防止 writer+critic 串通虚高通过（"摆烂"），监管者真正起到把关作用。
            if monitor_history and monitor_score > 0 and monitor_score < min_score:
                return {
                    "done": False,
                    "reason": (
                        f"全部{len(self.REQUIRED_SECTIONS)}个模块对抗胜利，"
                        f"但 monitor 独立评分{monitor_score:.2f}低于达标线{min_score:.2f}，"
                        f"不予流转，继续优化。"
                    ),
                }
            # v6.8.22: 断裂点5——P0 清零检查。即使 5 模块全胜，若存在未解决 critical P0，
            # 不予标达标流转，防止"带着致命问题出厂"。
            try:
                open_critical = prop_state.get("open_critical_issues", [])
                unresolved_criticals = [
                    e for e in (open_critical or [])
                    if isinstance(e, dict)
                    and e.get("round_resolved") is None
                    and not e.get("stale")
                    and (e.get("severity") or "").lower() == "critical"
                ]
                if unresolved_criticals:
                    sampled = ", ".join(
                        f"{e.get('section','?')}" for e in unresolved_criticals[:5]
                    )
                    return {
                        "done": False,
                        "reason": (
                            f"全部{len(self.REQUIRED_SECTIONS)}个模块对抗胜利，"
                            f"但仍有{len(unresolved_criticals)}条未解决 critical P0 "
                            f"（涉及：{sampled}{'...' if len(unresolved_criticals) > 5 else ''}），"
                            f"不予流转，继续优化。"
                        ),
                    }
            except Exception:
                pass  # 非关键路径，读取失败不阻断原有达标逻辑
            # v7.3.42 用户裁决：A 通道不再自动晋级——全部模块达标仅代表
            # "建议专家评审"已入队（见函数开头），晋级只保留 B 通道与人工验收。
            if _panel_enabled:
                return {
                    "done": False,
                    "reason": (
                        f"全部{len(self.REQUIRED_SECTIONS)}个模块对抗胜利"
                        f"（{','.join(passed_sections)}），A 通道已改为"
                        f"'建议专家评审'提醒，不自动晋级；等待人工或评审团确认。"
                    ),
                    "panel_prompt": prop_state.get("a_gate_panel_request"),
                }
            return {
                "done": True,
                "reason": f"全部{len(self.REQUIRED_SECTIONS)}个模块对抗胜利（{','.join(passed_sections)}）",
                "promotion_kind": "all_sections_passed",
            }

        # v6.8.16 改进1: 质量天花板检测（收敛检测）
        # 连续 3 轮分数 ≥0.85 且每轮提升 <2% → 自动晋级到 pending_review
        # v6.9.27: 收敛线随达标线整体上调（面上 0.85），防止低分课题绕过新标准
        # v6.9.57 结构性注记：本收敛线与程序化天花板体系冲突——AI 写作检测
        #   ceiling<0.9 档把综合分 cap 在 0.85，锚点"差距明显"档 cap 在 0.84，
        #   导致锚点达标前综合分无法连续 4 轮 ≥0.85（全量 32 轮实测 max 0.81，
        #   本分支零触发，健康检查多轮定性为死代码）。在锚点对比"达标"成为
        #   常态前，晋级的实际主路径是全模块对抗胜利 + 人工验收（dossier）。
        #   配套的次优平台检测见下方 SUBOPTIMAL_FLOOR。
        CONVERGENCE_SCORE = 0.85
        CONVERGENCE_ROUNDS = 3
        CONVERGENCE_DELTA = 0.02

        # v7.3.83: 平台 park（用户裁决 2026-11-15 token 治理④）——平台/
        # 收敛此前只挂 quality_warning，轮转照跑（bsv 实证 15 轮 0.80 原地，
        # 高轮次零收益空转）。高位平台且方法手册门未过线（晋级无路）时
        # 自动冻结轮转转人工；手册已过线不冻（正常晋级路径仍通）。
        def _park_if_gate_blocked() -> None:
            if section_passes.get("method_manual"):
                return
            prop_state["scheduler_frozen"] = True
            prop_state["scheduler_frozen_reason"] = (
                "平台转人工：高位平台且方法手册门未过线，轮转暂停——"
                "人工裁决（审核会话采纳 / 手册过线后解冻）")
        if len(score_history) >= CONVERGENCE_ROUNDS + 1:
            recent = score_history[-(CONVERGENCE_ROUNDS + 1):]
            # v6.9.62: 残缺维度轮（dims_partial，criter 维度解析不完整产生的
            # 残缺口径均值）打断连续性——不参与收敛判定，防止残缺分数
            # 触发自动晋级或污染平台检测。
            if not any(h.get("dims_partial") for h in recent):
                recent_scores = [h["score"] for h in recent]
                # v6.9.16 修复：窗口内全部轮次（含当前轮）都须 ≥0.80。
                # 原实现只约束前 3 轮（recent_scores[:-1]），"3 轮高位平台后
                # 当前轮骤降"（含伪分数污染，如实测 0.85→0.18）会被误判为
                # 质量收敛而自动晋级 pending_review，掩盖质量回退。
                if all(s >= CONVERGENCE_SCORE for s in recent_scores):
                    # 且每轮提升 <2%
                    deltas = [recent_scores[i + 1] - recent_scores[i] for i in range(len(recent_scores) - 1)]
                    if all(d < CONVERGENCE_DELTA for d in deltas):
                        # v6.10.3 F3: 收敛自动晋级降级为人工信号——本分支与
                        # 程序化天花板体系冲突（AI 检测 ceiling<0.9 档把综合分
                        # cap 在 0.85、锚点"差距明显"档 cap 在 0.84，全量 32
                        # 轮实测 max 0.81，零触发，健康检查多轮定性为死代码）。
                        # 即使未来天花板放开后变得可达，"自动晋级"也与
                        # "人工验收为主"的定位相悖（用户裁决 2026-09-09：
                        # 晋级条件偏松，收敛通道不应作为自动晋级口）。
                        # 改为与 SUBOPTIMAL_FLOOR 同款：只挂 quality_warning，
                        # 由人工评估是否晋级验收。落穿到后续逃生阀/未达标路径。
                        try:
                            prop_state["quality_warning"] = (
                                f"○ 质量收敛：连续{CONVERGENCE_ROUNDS}轮分数≥"
                                f"{CONVERGENCE_SCORE:.2f}且每轮提升<"
                                f"{CONVERGENCE_DELTA:.0%}（当前{last_score:.2f}），"
                                f"贴近天花板的高位平台，建议人工评估是否晋级验收"
                            )
                            _park_if_gate_blocked()
                            self._set_proposal_state(proposal_id, prop_state)
                        except Exception:
                            pass  # 状态写入失败不阻断后续判定

        # v6.9.57: 次优平台检测——收敛线 0.85 在锚点达标前结构性不可达
        # （见上方注记），本检测把"贴近天花板的平台化"转为有效人工信号：
        # 0.80-0.85 区间连续平台 → 不自动晋级，仅置 quality_warning，
        # 由人工评估是否提前晋级验收（人工验收为主定位）。
        SUBOPTIMAL_FLOOR = 0.80
        if len(score_history) >= CONVERGENCE_ROUNDS + 1:
            _recent_all = score_history[-(CONVERGENCE_ROUNDS + 1):]
            # v6.9.62: 残缺维度轮同样不参与平台检测（连续性被打断即不构成平台）
            if not any(h.get("dims_partial") for h in _recent_all):
                _recent = [h["score"] for h in _recent_all]
                if all(SUBOPTIMAL_FLOOR <= s < CONVERGENCE_SCORE for s in _recent):
                    _deltas = [_recent[i + 1] - _recent[i] for i in range(len(_recent) - 1)]
                    if all(abs(d) < CONVERGENCE_DELTA for d in _deltas):
                        try:
                            prop_state["quality_warning"] = (
                                f"○ 次优平台：连续{CONVERGENCE_ROUNDS}轮分数在"
                                f"{SUBOPTIMAL_FLOOR:.2f}-{CONVERGENCE_SCORE:.2f} 平台"
                                f"（当前{last_score:.2f}），贴近程序化天花板（AI检测/锚点绑定），"
                                f"自动提升空间有限，建议人工评估是否晋级验收"
                            )
                            _park_if_gate_blocked()
                            # v6.9.59 修复：_get_proposal_state 每次从磁盘新读
                            # （无缓存），not-done 返回路径若不显式落盘，警告只
                            # 改了内存副本即丢失——单测 mock 返回同一 dict 引用
                            # 曾掩盖此问题，生产端 review_dossier 永远读不到信号。
                            self._set_proposal_state(proposal_id, prop_state)
                        except Exception:
                            pass  # 状态写入失败不阻断达标判定

        # v7.2.24 通道 B（验收线晋级）：双通道晋级体系主通道（用户裁决
        # 2026-10-13「执行」）。诊断实证：几个月 200 轮全量统计中
        # content 达标 0/42、scheme 0/40（历史最高 0.83/0.84），常规
        # 「5 模块全 ≥0.90 + monitor ≥0.90」路径在 LLM critic 锚定
        # 体系（0.90=五项核查全过的亲审级）下数学上不可达——全局仅
        # 3 次 ≥0.90 且全为 references 2 维口径；而 monitor 独立口径
        # 已达 0.83-0.86，质量并未停滞。archived 终态本就只收人工
        # 审查通过课题（v6.10.50 用户裁决），机器 0.90 线应定位为
        # 「免检通道」而非唯一通道。
        #
        # v7.2.31 方案 C（用户裁决 2026-10-18「直接走方案 C」）：
        # 旧版「综合分 ≥ 0.82」数学上不可达——section_4d 中位数 0.78
        # （rigor 0.70 拖后腿，innovation 0.85/feasibility 0.82 已达标），
        # 旧阈值把所有"基本接近"（39/43 锚定结论）的课题全部卡住。
        # 改造语义：从「单值综合分门」改为「4 维加权门 + 双维独立门 +
        # rigor 软底线 + 锚点背书 + dossier 3 档把关兜底」，数学上对
        # 齐 critic 锚定改革后真实评分分布。
        #
        # v7.2.31 实证评估（11 课题 0/11 触发）→ 调整阈值（v7.2.31c）：
        # - 综合分门槛 0.82 → 0.74（贴近真实平台带）
        # - 下降容忍 0.5% → 5%（单轮 critic 评分波动真实存在 ±5%）
        # - feasibility 0.82 → 0.78（贴近真实中位）
        # - 排除历史 critical 累积（v6/v7.x 累积的 11-19 条不该阻断）
        # - rigor 0.70 → 0.65（更接近过 3 档的下限）
        # 调整后：4/11 首批触发（attosecond/berry/order-param/ssh-weyl），
        # 4/11 待轮次（bsv/houston/moire/new-idea 1-2 周就绪），
        # 3/11 单条件卡（mos2 feas 0.77 差 0.01 / qgi/key-transient 下降超 5%）。
        #
        # 新通道语义（v7.2.31c）：
        #   条件 1：连续 3 轮（4 维章节口径）综合分 ≥ 0.74（平台带 - 4% 容忍）
        #   条件 2：单轮下降 ≤ 5%（LLM 评分真实波动 3-7%）
        #   条件 3：innovation ≥ 0.82（创新独立门——最稳维度）
        #   条件 4：feasibility ≥ 0.78（可行性独立门——贴真实中位）
        #   条件 5：rigor ≥ 0.65（不是 0.80！与 critic 5 项清单
        #           「过三档 0.70+」档位下限对齐 + 容忍）
        #   条件 6：最近一轮 anchor_conclusion ≥ "基本接近"
        #   条件 7：monitor 独立分 ≥ 0.76
        #   条件 8：无未解决 critical P0（v6.8.22 防线）
        # 满足以上全部 → 转 pending_review 人工验收（dossier 三档把关，
        # 一键采纳仍受 approve_gate 约束；dossier 本身已设三档预审，
        # 不达标课题在此阶段会被标 attention 而非 adopt）。
        ACCEPT_LINE = 0.74
        ACCEPT_ROUNDS = 3
        ACCEPT_MONITOR_FLOOR = 0.76
        ACCEPT_DECLINE_TOL = 0.05
        ACCEPT_INNOVATION_FLOOR = 0.82
        ACCEPT_FEASIBILITY_FLOOR = 0.78
        ACCEPT_RIGOR_FLOOR = 0.65
        ACCEPT_ANCHOR_MIN = "基本接近"  # 包含"达标"/"基本接近"，挡"差距明显"
        if (
            len(score_history) >= ACCEPT_ROUNDS
            and monitor_score >= ACCEPT_MONITOR_FLOOR
        ):
            _acc_win = score_history[-ACCEPT_ROUNDS:]
            if not any(h.get("dims_partial") for h in _acc_win):
                _acc_scores = [h["score"] for h in _acc_win]
                _acc_deltas = [
                    _acc_scores[i + 1] - _acc_scores[i]
                    for i in range(len(_acc_scores) - 1)
                ]
                if (
                    all(s >= ACCEPT_LINE for s in _acc_scores)
                    and all(d >= -ACCEPT_DECLINE_TOL for d in _acc_deltas)
                ):
                    # v7.2.31 方案 C：4 维加权门 + 双维独立门
                    # 取最近一轮非 partial 的 dim_scores（v7.2.30 看板 4 维化
                    # 后所有 4 维 section 轮都带 dim_scores 字段）
                    _last_dims = None
                    for _h in reversed(_acc_win):
                        if _h.get("dim_scores") and not _h.get("dims_partial"):
                            _last_dims = _h.get("dim_scores", {})
                            break
                    _innovation = _last_dims.get("innovation", 0) if _last_dims else 0
                    _feasibility = _last_dims.get("feasibility", 0) if _last_dims else 0
                    _rigor = _last_dims.get("rigor", 0) if _last_dims else 0
                    # 最近一轮 anchor
                    _last_anchor = ""
                    for _h in reversed(_acc_win):
                        if _h.get("anchor_conclusion"):
                            _last_anchor = _h.get("anchor_conclusion", "")
                            break

                    _dim_pass = (
                        _innovation >= ACCEPT_INNOVATION_FLOOR
                        and _feasibility >= ACCEPT_FEASIBILITY_FLOOR
                        and _rigor >= ACCEPT_RIGOR_FLOOR
                    )
                    _anchor_pass = _last_anchor in ("基本接近", "达标", "")
                    # _last_anchor 为空时默认通过（兼容旧数据，4 维 dict
                    # 在 v7.2.18 评分改革后才有 anchor_conclusion 字段——
                    # 部分历史轮次可能缺；缺时保守不阻挡，让 monitor 与
                    # 4 维字典把关）
                    # v7.3.0: 验收线晋级加手册门——手册未过线（未达开工
                    # 就绪）不适用"稳定平台+monitor 背书"快速通道
                    _manual_pass = bool(section_passes.get("method_manual"))

                    if _dim_pass and _anchor_pass and _manual_pass:
                        # v6.8.22 同款防线：带未解决 critical P0 不予流转
                        # （防止"带着致命问题出厂"），落穿到后续路径继续优化
                        try:
                            _acc_crit = prop_state.get("open_critical_issues", [])
                            _acc_unresolved = [
                                e for e in (_acc_crit or [])
                                if isinstance(e, dict)
                                and e.get("round_resolved") is None
                                and not e.get("stale")
                                and (e.get("severity") or "").lower() == "critical"
                            ]
                        except Exception:
                            _acc_unresolved = []
                        if not _acc_unresolved:
                            _traj = "→".join(f"{s:.2f}" for s in _acc_scores)
                            return {
                                "done": True,
                                "reason": (
                                    f"验收线晋级（方案 C）：连续{ACCEPT_ROUNDS}轮"
                                    f"章节口径≥{ACCEPT_LINE:.2f}无下降（{_traj}），"
                                f"4维加权 innov={_innovation:.2f}/"
                                f"feas={_feasibility:.2f}/rigor={_rigor:.2f}"
                                f"全过门槛，anchor={_last_anchor or '缺'}，"
                                f"手册就绪度已过线，"
                                f"monitor独立分{monitor_score:.2f}≥"
                                f"{ACCEPT_MONITOR_FLOOR:.2f}，"
                                f"转人工验收（dossier 三档把关）"
                                ),
                                "promotion_kind": "acceptance_line",
                                "quality_warning": None,
                            }

        # v6.10.14 + v7.1.8: 平台期转评审团（分层策略）——0.70-0.85 主平台带是
        # "逃生阀晋级→reject_lean→人工退回"无效循环的主体（实测 09-13
        # 复盘：133 次评分仅 3 次模块通过、0 次质量晋级，3 次晋级全靠
        # 最大轮数逃生阀且全被退回；平台带课题每课题末端空转 30-40h
        # LLM 机时）。连续 4 轮评分在 [0.70, 0.85) 且每轮 |Δ|<2% 即判
        # 平台期：置 panel_review_requested，调度跳过自动循环（机时让
        # 给爬坡型课题），进人工队列等评审团深度修改；人工处理完由
        # clear_panel_request 清除恢复自动循环。
        #
        # v7.1.8 用户裁决（基于"产出研究人员可执行的课题"目标）：
        # r3 完成即触发评审团（不依赖分数窗口，r3 是质量天花板自然信号）。
        # 旧"4 轮原地踏步"检测在 score_history 跨重置/跨状态后窗口破坏，
        # 看板 5 个平台期课题 panel_review_requested 0 次命中——这条路径
        # 几乎不生效。新路径以"rounds>=3 + 本轮完成"为硬触发，无论分数。
        # 已通过评审团的课题由 clear_panel_request 清标志 + 评审团修改后
        # 重置 rounds 进入下一轮评审周期。
        PANEL_FLOOR = 0.70
        PANEL_ROUNDS = 4
        if (
            len(score_history) >= PANEL_ROUNDS
            and not prop_state.get("panel_review_requested")
        ):
            _pw = score_history[-PANEL_ROUNDS:]
            if not any(h.get("dims_partial") for h in _pw):
                _ps = [h["score"] for h in _pw]
                if all(PANEL_FLOOR <= s < CONVERGENCE_SCORE for s in _ps):
                    _pd = [_ps[i + 1] - _ps[i] for i in range(len(_ps) - 1)]
                    if all(abs(d) < CONVERGENCE_DELTA for d in _pd):
                        try:
                            prop_state["panel_review_requested"] = True
                            # v6.10.15: 时间戳驱动催办——队列 waiting_hours
                            # 与 72h escalate 依赖此字段，缺失则评审团请求
                            # 永远静默挂着无人推动
                            prop_state["panel_requested_at"] = now_utc()
                            prop_state["panel_review_reason"] = (
                                f"主平台带：连续{PANEL_ROUNDS}轮评分在"
                                f"{PANEL_FLOOR:.2f}-{CONVERGENCE_SCORE:.2f} 且每轮"
                                f"|Δ|<{CONVERGENCE_DELTA:.0%}（当前{last_score:.2f}），"
                                f"自动循环边际收益趋零，转评审团深度修改"
                            )
                            self._set_proposal_state(proposal_id, prop_state)
                        except Exception:
                            pass

        # v7.1.8: r3 完成即触发评审团（不依赖分数窗口）。
        # 触发条件：
        #   - 当前 rounds >= 3（即已完成 r3，本轮为 r4 或后续）
        #   - 本轮 rounds 已推进（rounds 比 _check_done 进入时的快照多 1）
        #   - 尚未请求过 panel（避免重复触发）
        # 效果：r3 → r4 切换的瞬间置 panel_review_requested，调度层
        #   （_focus_proposal_for_slot v6.10.14）跳过自动循环，机时让
        #   位给爬坡型课题；评审团深度修改 + review_dossier + 7 天人工
        #   否决窗口后，clear_panel_request 清标志，rounds 重置进入
        #   下一轮评审周期。
        _PANEL_R3_TRIGGER = 3
        if (
            rounds >= _PANEL_R3_TRIGGER
            and not prop_state.get("panel_review_requested")
            and not prop_state.get("panel_review_completed_for_round")
        ):
            try:
                prop_state["panel_review_requested"] = True
                prop_state["panel_requested_at"] = now_utc()
                prop_state["panel_review_reason"] = (
                    f"v7.1.8 r{_PANEL_R3_TRIGGER} 完成触发评审团（不依赖分数窗口）："
                    f"已完成{rounds}轮自动优化（当前{last_score:.2f}），"
                    f"按用户目标'产出研究人员可执行的课题'转入评审团深度修改"
                )
                self._set_proposal_state(proposal_id, prop_state)
                if _log:
                    _log.info(
                        f"[{proposal_id}] r3 触发评审团（v7.1.8），"
                        f"rounds={rounds}，分数={last_score:.2f}"
                    )
            except Exception:
                pass

        # v6.8.16 改进1: 质量下降检测
        # 连续 3 轮分数下降 → 标记 quality_declining，附加质量警告
        DECLINE_ROUNDS = 3
        if len(score_history) >= DECLINE_ROUNDS + 1:
            _decline_window = score_history[-(DECLINE_ROUNDS + 1):]
            # v6.9.62: 残缺维度轮不参与下降判定（残缺口径均值骤降≠质量下降）
            if not any(h.get("dims_partial") for h in _decline_window):
                recent_scores = [h["score"] for h in _decline_window]
                deltas = [recent_scores[i + 1] - recent_scores[i] for i in range(len(recent_scores) - 1)]
                if all(d < 0 for d in deltas[-DECLINE_ROUNDS:]):
                    quality_warning = (
                        f"⚠ 质量下降: 连续{DECLINE_ROUNDS}轮分数下降"
                        f"（{recent_scores[-DECLINE_ROUNDS-1]:.2f}→{recent_scores[-1]:.2f}）。"
                        f"建议人工干预检查优化方向。"
                    )
                    # v7.3.0: 手册未就绪显式标注（开工前提，人工裁量必看）
                    if not section_passes.get("method_manual"):
                        quality_warning += " ⚠ 方法手册未达开工就绪（L<3），课题尚不可正式开始。"
                    return {
                        "done": True,
                        "reason": f"连续{DECLINE_ROUNDS}轮质量下降，暂停自动优化",
                        "quality_warning": quality_warning,
                        "promotion_kind": "quality_declining",
                    }

        # 条件2：连续N轮无提升（逃生阀）
        no_improve_limit = DEFAULT_NO_IMPROVEMENT_LIMIT
        if len(score_history) >= no_improve_limit + 1:
            recent_scores = [h["score"] for h in score_history[-(no_improve_limit + 1):]]
            deltas = [recent_scores[i + 1] - recent_scores[i] for i in range(len(recent_scores) - 1)]
            if all(d <= 0 for d in deltas):
                passed_str = f"（已通过{len(passed_sections)}/{len(self.REQUIRED_SECTIONS)}模块）"
                # v6.8.3: 逃生阀触发时附加质量警告
                # v6.10.3 F1: 警告比较改用整篇有效分（monitor 独立分优先，
                # 其次最近 4 维章节分），不再用 last_score（其系统性等于
                # references 2 维口径单模块分，会豁免警告造成达标误读）。
                quality_warning = ""
                _eff = self._effective_score(prop_state, monitor_score)
                if _eff["score"] < min_score:
                    quality_warning = (
                        f"⚠ 质量警告: 整篇有效分{_eff['score']:.2f}（{_eff['caliber']}）"
                        f"低于达标线{min_score:.2f}。"
                        f"已通过{len(passed_sections)}/{len(self.REQUIRED_SECTIONS)}模块。"
                        f"monitor评分{monitor_score:.2f}。建议人工审核。"
                    )
                # v7.3.0: 逃生阀晋级时手册未就绪显式标注（无论分高低）
                if not section_passes.get("method_manual"):
                    quality_warning += (
                        " ⚠ 方法手册未达开工就绪（L<3），课题尚不可正式开始。"
                    )
                return {
                    "done": True,
                    "reason": f"连续{no_improve_limit}轮无显著提升{passed_str}",
                    "quality_warning": quality_warning if quality_warning else None,
                    "promotion_kind": "escape_no_improvement",
                }

        # 条件3：达到最大轮数（逃生阀）
        if rounds >= max_rounds:
            passed_str = f"（已通过{len(passed_sections)}/{len(self.REQUIRED_SECTIONS)}模块）"
            quality_warning = ""
            # v6.10.3 F1: 同条件2——用整篇有效分比较（见上方注记）。
            _eff = self._effective_score(prop_state, monitor_score)
            if _eff["score"] < min_score:
                quality_warning = (
                    f"⚠ 质量警告: 达到最大轮数{max_rounds}，整篇有效分"
                    f"{_eff['score']:.2f}（{_eff['caliber']}）低于达标线{min_score:.2f}。"
                    f"已通过{len(passed_sections)}/{len(self.REQUIRED_SECTIONS)}模块。"
                    f"monitor评分{monitor_score:.2f}。建议人工审核。"
                )
            # v7.3.0: 逃生阀晋级时手册未就绪显式标注（无论分高低）
            if not section_passes.get("method_manual"):
                quality_warning += (
                    " ⚠ 方法手册未达开工就绪（L<3），课题尚不可正式开始。"
                )
            return {
                "done": True,
                "reason": f"达到最大轮数{max_rounds}{passed_str}",
                "quality_warning": quality_warning if quality_warning else None,
                "promotion_kind": "escape_max_rounds",
            }

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
        # v6.9.92: 同步尊重 per-proposal 轮次覆盖（见 check_completion 注记）
        try:
            _ovr_a = int(prop_state.get("max_rounds_override") or 0)
        except (TypeError, ValueError):
            _ovr_a = 0
        _max_rounds_a = _ovr_a if _ovr_a > 0 else DEFAULT_MAX_ROUNDS

        while rounds_done < _max_rounds_a:
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
            reason=f"达到最大轮数{_max_rounds_a}，当前分数{last_result.get('score_after', 0):.2f}"
        )
        return {
            "success": True,
            "advanced": True,
            "rounds": rounds_done,
            "final_score": last_result.get("score_after", 0),
            "reason": "达到最大轮数",
            "transition": transition_result,
        }
