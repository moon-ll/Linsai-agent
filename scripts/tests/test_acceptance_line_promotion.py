#!/usr/bin/env python3
"""
test_acceptance_line_promotion.py — 通道 B（验收线晋级）回归测试（v7.2.24）

覆盖 _check_done 通道 B 分支的边界（双通道晋级体系主通道）：
    1. 正向触发：末 3 轮章节口径 ≥0.82 无下降 + monitor ≥0.80 → done=True
       + promotion_kind=acceptance_line（转人工验收）
    2. monitor 不足：分数达标但 monitor 0.75 < 0.80 → 不触发（落穿）
    3. 分数不足：末 3 轮 [0.81, 0.82, 0.83]（首轮 0.81 < 0.82）→ 不触发
    4. 下降超容忍：[0.85, 0.84, 0.82]（deltas -0.01 超 0.5% 容忍）→ 不触发
    4b. 微降在容忍内：[0.83, 0.826, 0.83]（delta -0.004 < 0.005）→ 触发
    5. dims_partial 打断：窗口含残缺维度轮 → 不触发
    6. P0 未解决：分数+monitor 达标但存在 unresolved critical → 不晋级
    7. references 异口径不参与窗口（沿用 v6.9.78 过滤）
    8. 现有语义兼容：monitor_history 为空（monitor_score=0）→ 通道 B
       不触发，次优平台/收敛警告路径行为不变

背景（用户裁决 2026-10-13「执行」）：几个月 200 轮实测 content 达标
0/42、scheme 0/40（历史最高 0.83/0.84），常规「5 模块全 ≥0.90」路径
在 LLM critic 锚定体系下数学上不可达；monitor 独立口径已达 0.83-0.86。
通道 B = 稳定验收线平台 + monitor 背书 → pending_review 人工验收。

注意：
    本测试不调用 hermes/LLM，仅验证达标判定的数据逻辑。

用法示例：
    python3 scripts/tests/test_acceptance_line_promotion.py
"""

import copy
import sys
import importlib

from test_runner import TestSuite, create_isolated_env


class AcceptanceLinePromotionTests(TestSuite):
    def __init__(self):
        super().__init__("通道B验收线晋级测试")
        self.tmp_root = None
        self._comp = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        for mod_name in [
            "proposal_lifecycle.completion",
            "proposal_lifecycle",
            "proposal_sections",
        ]:
            if mod_name in sys.modules:
                del sys.modules[mod_name]
        importlib.import_module("proposal_lifecycle.completion")
        from proposal_lifecycle.completion import CompletionMixin

        # 最小实例：mock 状态读写（磁盘新读语义，与
        # test_quality_ceiling_convergence 同款），不触发 LLM / 日志。
        class _StateHolder:
            def __init__(self):
                self._disk = {}
                self.set_calls = []

            def _get_proposal_state(self, proposal_id):
                return copy.deepcopy(self._disk.get(proposal_id))

            def _set_proposal_state(self, proposal_id, state):
                self._disk[proposal_id] = copy.deepcopy(state)
                self.set_calls.append(proposal_id)
                return True

        class _FakeComp(CompletionMixin, _StateHolder):
            def __init__(self):
                _StateHolder.__init__(self)

        self._comp = _FakeComp()

    def teardown(self):
        pass

    def run_tests(self):
        comp = self._comp
        threshold = {"min_overall_score": 0.90}
        sections = ["rationale", "content", "scheme", "full_review", "references"]
        # v7.3.0: 通道 B 加手册门——夹具默认手册过线（单独用例验证未过线拦截）
        sections = sections + ["method_manual"]

        def _state(scores, monitor=0.0, focus=None, crit=None,
                   dims=None, anchor=None, high_issues=2, manual_pass=True):
            """构造 prop_state。focus 为各轮 focus_section 列表（缺省全
            content 口径）；crit 为 open_critical_issues 覆盖。

            v7.2.31 方案 C 升级：默认填 dim_scores（双维 0.84/rigor 0.78/
            expression 0.78/anchor="基本接近"/high_issues=2），让历史正
            向测试不需要手动传这些字段。
            """
            hist = []
            for i, s in enumerate(scores):
                h = {
                    "score": s,
                    "caliber": "section_4d",
                    "dims_partial": False,
                    "high_issues": high_issues,
                }
                if focus:
                    h["focus_section"] = focus[i]
                # 缺省 dim_scores：综合分推 4 维为 0.84/0.84/0.78/0.78
                if dims is not None:
                    h["dim_scores"] = dims
                else:
                    h["dim_scores"] = {
                        "innovation": 0.84, "feasibility": 0.84,
                        "rigor": 0.78, "expression": 0.78,
                    }
                h["anchor_conclusion"] = anchor if anchor is not None else "基本接近"
                hist.append(h)
            st = {
                "status": "optimizing",
                "score_history": hist,
                "last_score": scores[-1],
                "section_passes": {**{k: False for k in sections[:-1]},
                                   "method_manual": manual_pass},
                "optimization_rounds": len(scores),
                "monitor_history": (
                    [{"monitor_independent_score": monitor}] if monitor > 0 else []
                ),
                "open_critical_issues": crit or [],
            }
            comp._set_proposal_state("p1", st)

        # ---------- 1. 正向触发：稳定平台 + monitor 背书 → 验收线晋级 ----------
        _state([0.79, 0.82, 0.83, 0.84], monitor=0.84)
        res1 = comp._check_done("p1", threshold)
        self.assert_eq(res1["done"], True, "稳定 0.82+ 平台 + monitor 0.84 应触发验收线晋级")
        self.assert_eq(
            res1.get("promotion_kind"), "acceptance_line",
            "晋级方式应为 acceptance_line")
        self.assert_in("验收线", res1["reason"], "reason 应标注验收线语义")
        self.assert_in("人工验收", res1["reason"], "reason 应说明转人工验收")
        self.assert_eq(
            res1.get("quality_warning"), None,
            "验收线晋级不挂质量警告（dossier 预审把关）")

        # ---------- 2. monitor 不足：分数达标但 monitor 0.75 → 不触发 ----------
        _state([0.79, 0.82, 0.83, 0.84], monitor=0.75)
        res2 = comp._check_done("p1", threshold)
        self.assert_eq(res2["done"], False, "monitor 0.75 < 0.80 不触发通道 B")

        # ---------- 3. 分数不足：v7.2.24 旧版 末 3 轮首项 0.81 < 0.82 不触发；
        # v7.2.31 方案 C ACCEPT_LINE 降为 0.78，0.81 ≥ 0.78 → 触发
        # （同时 4 维加权 rigor 0.78 ≥ 0.70 软底线 + monitor 0.84 + anchor 缺省
        # 默认通过 → 整体满足方案 C 全部条件）
        _state([0.78, 0.81, 0.82, 0.83], monitor=0.84)
        res3 = comp._check_done("p1", threshold)
        self.assert_eq(
            res3["done"], True,
            "v7.2.31 方案 C：0.81 ≥ ACCEPT_LINE(0.78) 触发（语义变更，原 0.82 阈值下线）")

        # ---------- 4. 下降超容忍：v7.2.31c 容忍 5% 噪声（原 0.5% 太严） ----------
        # 用 [0.85, 0.78, 0.74] delta = -0.07/-0.04，min delta -0.07 超 5% 容忍
        _state([0.79, 0.85, 0.78, 0.74], monitor=0.84)
        res4 = comp._check_done("p1", threshold)
        self.assert_eq(
            res4["done"], False,
            "下降 -0.07 超 5% 噪声容忍（基于 0.85），不构成稳定平台")

        # ---------- 4b. 微降在容忍内：[0.85, 0.84, 0.82] delta -0.01 → 触发 ----------
        _state([0.79, 0.85, 0.84, 0.83], monitor=0.82)
        res4b = comp._check_done("p1", threshold)
        self.assert_eq(
            res4b["done"], True,
            "v7.2.31c 容忍 5%：delta -0.01 在容忍内，视为平台触发晋级")

        # ---------- 5. dims_partial 打断：窗口含残缺轮 → 不触发 ----------
        _state([0.79, 0.82, 0.83, 0.84], monitor=0.84)
        st5 = comp._get_proposal_state("p1")
        st5["score_history"][-1]["dims_partial"] = True
        comp._set_proposal_state("p1", st5)
        res5 = comp._check_done("p1", threshold)
        self.assert_eq(
            res5["done"], False,
            "残缺维度轮打断连续性，不触发通道 B（防残缺口径误晋级）")

        # ---------- 6. P0 未解决：达标但有 unresolved critical → 不晋级 ----------
        crit6 = [{
            "severity": "critical",
            "section": "content",
            "round_resolved": None,
            "stale": False,
        }]
        _state([0.79, 0.82, 0.83, 0.84], monitor=0.84, crit=crit6)
        res6 = comp._check_done("p1", threshold)
        self.assert_eq(
            res6["done"], False,
            "带未解决 critical P0 不予流转（防带着致命问题出厂）")
        # 6b. 对照：critical 已解决（round_resolved 非 None）→ 正常触发
        crit6b = [{
            "severity": "critical",
            "section": "content",
            "round_resolved": 3,
            "stale": False,
        }]
        _state([0.79, 0.82, 0.83, 0.84], monitor=0.84, crit=crit6b)
        res6b = comp._check_done("p1", threshold)
        self.assert_eq(
            res6b["done"], True,
            "已解决的 critical 不阻断通道 B")

        # ---------- 7. references 异口径不参与窗口（v6.9.78 过滤沿用） ----------
        # 序列 [0.75, 0.50(refs), 0.73, 0.73]：references 条目被过滤后
        # 窗口为 [0.75, 0.73, 0.73]（章节口径），min=0.73 < 0.74 → 不触发
        _state(
            [0.75, 0.50, 0.73, 0.73],
            monitor=0.84,
            focus=["content", "references", "scheme", "full_review"],
        )
        res7 = comp._check_done("p1", threshold)
        self.assert_eq(
            res7["done"], False,
            "references 过滤后章节窗口 min=0.73 < 0.74，不触发通道 B")

        # ---------- 8. monitor_history 为空 → 通道 B 不触发（兼容存量语义） ----------
        # 存量次优平台/收敛警告测试（test_quality_ceiling_convergence 1/5）
        # 均 monitor_history=[]：通道 B 不抢路径，原行为不变。
        _state([0.79, 0.81, 0.82, 0.82, 0.82], monitor=0.0)
        res8 = comp._check_done("p1", threshold)
        self.assert_eq(
            res8["done"], False,
            "monitor 缺位（未跑 meta-review）不触发通道 B，次优平台警告路径不变")
        warned8 = comp._get_proposal_state("p1").get("quality_warning") or ""
        self.assert_in(
            "次优平台", warned8,
            "次优平台警告照常写入（通道 B 不破坏存量信号）")

        # ============================================================
        # v7.2.31 方案 C：4 维加权门 + 双维独立门 + 锚点背书 + 软底线
        # ============================================================

        # ---------- 9. 方案 C 正向：综合 0.78 + 双维 0.84 + rigor 0.78 + 基本接近 → 触发 ----------
        # 关键场景：旧版 0.82 不通过，方案 C 0.78 + 4 维加权通过
        _state([0.78, 0.79, 0.80], monitor=0.80)
        res9 = comp._check_done("p1", threshold)
        self.assert_eq(res9["done"], True, "方案 C 综合 0.78+ 双维达标触发")
        self.assert_eq(res9.get("promotion_kind"), "acceptance_line", "晋级方式 acceptance_line")
        self.assert_in("方案 C", res9["reason"], "reason 应标注方案 C 语义")

        # ---------- 10. 方案 C v7.2.31c：rigor 0.60 < 0.65 软底线 → 不通过 ----------
        _state([0.78, 0.79, 0.80], monitor=0.80, dims={
            "innovation": 0.85, "feasibility": 0.84, "rigor": 0.60, "expression": 0.74
        })
        res10 = comp._check_done("p1", threshold)
        self.assert_eq(res10["done"], False, "rigor 0.60 < 软底线 0.65 不触发")

        # ---------- 11. 方案 C v7.2.31c：feasibility 0.75 < 0.78 双维独立门 → 不通过 ----------
        _state([0.78, 0.79, 0.80], monitor=0.80, dims={
            "innovation": 0.85, "feasibility": 0.75, "rigor": 0.75, "expression": 0.74
        })
        res11 = comp._check_done("p1", threshold)
        self.assert_eq(res11["done"], False, "feasibility 0.75 < 双维独立门 0.78 不触发")

        # ---------- 12. 方案 C：anchor="差距明显" → 不通过（真差档背书） ----------
        _state([0.78, 0.79, 0.80], monitor=0.80, anchor="差距明显")
        res12 = comp._check_done("p1", threshold)
        self.assert_eq(res12["done"], False, "anchor='差距明显' 挡真差档")

        # ---------- 13. 方案 C：anchor="达标" → 通过（最优档背书） ----------
        _state([0.78, 0.79, 0.80], monitor=0.80, anchor="达标")
        res13 = comp._check_done("p1", threshold)
        self.assert_eq(res13["done"], True, "anchor='达标' 通过方案 C")

        # ---------- 14. 方案 C v7.2.31c：high_issues 不再阻断（dossier 3 档把关兜底） ----------
        # v7.2.31c 决策：high_issues 由 dossier 3 档 attention 提示，不阻断通道 B
        # （避免 ssh-weyl 13 条 historical high 阻断；但 critical 阻断仍保留）
        _state([0.78, 0.79, 0.80], monitor=0.80, high_issues=4)
        res14 = comp._check_done("p1", threshold)
        self.assert_eq(res14["done"], True, "high_issues 不阻断通道 B（v7.2.31c）")

        # ---------- 15. 方案 C：anchor 缺省（v7.2.18 之前数据）→ 默认通过 ----------
        # 旧数据可能没 anchor_conclusion 字段——保守通过，让 monitor+4 维把关
        _state([0.78, 0.79, 0.80], monitor=0.80, anchor="")
        res15 = comp._check_done("p1", threshold)
        self.assert_eq(res15["done"], True, "anchor 缺省时默认通过（兼容旧数据）")

        # ---------- 16. v7.3.0 手册门：手册未过线 → 通道 B 不触发 ----------
        # 用户裁决 2026-11-02：手册就绪度决定课题可否开工——稳定平台 +
        # monitor 背书也不能在手册未过线时快速晋级
        _state([0.78, 0.79, 0.80], monitor=0.84, manual_pass=False)
        res16 = comp._check_done("p1", threshold)
        self.assert_eq(res16["done"], False, "手册未过线应拦截通道 B（v7.3.0）")


if __name__ == "__main__":
    import time
    suite = AcceptanceLinePromotionTests()
    suite.setup()
    t0 = time.time()
    suite.run_tests()
    suite.teardown()
    suite.duration = time.time() - t0
    from test_runner import print_report
    print_report([suite])
