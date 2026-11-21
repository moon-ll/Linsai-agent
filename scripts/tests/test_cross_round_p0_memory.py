#!/usr/bin/env python3
"""
test_cross_round_p0_memory.py — P0 跨轮持久化回归测试（v6.8.22）

覆盖 5 个断裂点的修复：
    断裂点3：_update_open_critical_issues 持久化逻辑（收录/去重/标记解决/上限）
    断裂点1：_build_p0_memory_text 供 critic 注入（exclude_resolved=True）
    断裂点2：_build_p0_memory_text 供 writer 注入（exclude_resolved=False）
    断裂点4：writer section_focus 中存在未解决 P0 时放宽跨章节限制
    断裂点5：completion._check_done 在 5 模块全胜但存在未解决 critical P0 时不达标

注意：
    本测试不调用 hermes/LLM，仅验证跨轮记忆的数据逻辑与达标判定。
"""

import sys
import importlib

from test_runner import TestSuite, create_isolated_env


class CrossRoundP0MemoryTests(TestSuite):
    def __init__(self):
        super().__init__("P0 跨轮持久化测试")
        self.tmp_root = None
        self._opt = None
        self._comp = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        for mod_name in [
            "proposal_lifecycle.optimize",
            "proposal_lifecycle.completion",
            "proposal_lifecycle",
            "proposal_sections",
        ]:
            if mod_name in sys.modules:
                del sys.modules[mod_name]
        importlib.import_module("proposal_lifecycle.optimize")
        importlib.import_module("proposal_lifecycle.completion")
        from proposal_lifecycle.optimize import OptimizeMixin
        from proposal_lifecycle.completion import CompletionMixin

        # 最小实例：mock 状态读写，不触发 LLM / 日志
        class _StateHolder:
            def __init__(self):
                self._state = {"open_critical_issues": []}

            def _get_proposal_state(self, proposal_id):
                return self._state

            def _set_proposal_state(self, proposal_id, state):
                self._state = state
                return True

        class _FakeOpt(OptimizeMixin, _StateHolder):
            def __init__(self):
                _StateHolder.__init__(self)

        class _FakeComp(CompletionMixin, _StateHolder):
            def __init__(self):
                _StateHolder.__init__(self)

        self._opt = _FakeOpt()
        self._comp = _FakeComp()

    def teardown(self):
        pass

    def run_tests(self):
        opt = self._opt

        # ---------- 断裂点3：持久化逻辑 ----------
        # 3.1 收录 critical/high，忽略 medium/low
        issues = [
            {"severity": "critical", "line": "指标口径不一致：R1 中翻转效率 0.5% 与 R3 的 2% 矛盾"},
            {"severity": "high", "line": "理论框架未注明适用条件与失效边界"},
            {"severity": "medium", "line": "建议补充过渡句"},
            {"severity": "low", "line": "个别标点"},
        ]
        merged = opt._update_open_critical_issues("p1", issues, current_round=1, focus_section_key="rationale")
        self.assert_eq(len(merged), 2, "仅收录 critical/high，medium/low 不入库")
        self.assert_eq({
            e["severity"] for e in merged
        }, {"critical", "high"}, "收录的严重程度为 critical 和 high")

        # 3.2 去重：下一轮同样措辞（相似键一致）应合并而非新增
        issues2 = [
            {"severity": "critical", "line": "指标口径不一致：R1 中翻转效率 0.5% 与 R3 的 2% 矛盾"},
        ]
        merged2 = opt._update_open_critical_issues("p1", issues2, current_round=2, focus_section_key="rationale")
        self.assert_eq(len(merged2), 2, "同问题跨轮合并，不重复新增")
        critical_entry = next(e for e in merged2 if e["severity"] == "critical")
        self.assert_eq(critical_entry["last_seen_round"], 2, "去重后更新 last_seen_round")
        self.assert_eq(critical_entry["round_resolved"], None, "本轮仍出现则保持未解决")

        # 3.3 标记解决：本轮不再出现则标记 round_resolved
        issues3 = [
            {"severity": "high", "line": "理论框架未注明适用条件与失效边界"},
        ]
        merged3 = opt._update_open_critical_issues("p1", issues3, current_round=3, focus_section_key="rationale")
        critical_entry3 = next(e for e in merged3 if e["severity"] == "critical")
        self.assert_eq(critical_entry3["round_resolved"], 3, "本轮未复现 → 标记为已解决")

        # 3.4 相似键：去除空白标点、小写、截断
        k1 = opt._issue_similarity_key("指标口径不一致：翻转效率 0.5%。")
        k2 = opt._issue_similarity_key("指标口径不一致,翻转效率 0.5%")
        self.assert_eq(k1, k2, "相似键忽略标点/空白差异")

        # 3.5 v6.9.37 回归：跨章节 critic 调用不得误标其他章节的未解决 P0
        # 背景：一轮内 rationale→content→scheme→full_review→references 共 5 次
        # critic 调用共享同一 open_critical_issues；原实现把"本轮未复现"按全
        # 章节口径判定，后续章节调用会把先前章节刚入库的 P0 误标已解决
        # （运行时实证：6 课题全部条目 round_resolved == first_seen_round）。
        merged4 = opt._update_open_critical_issues(
            "p1",
            [{"severity": "critical", "line": "content 章节自身的新问题X"}],
            current_round=4,
            focus_section_key="content",
        )
        self.assert_eq(len(merged4), 3, "content 新问题入库，历史条目不丢失")
        high_entry = next(e for e in merged4 if e["severity"] == "high")
        self.assert_eq(
            high_entry["round_resolved"], None,
            "content 章节 critic 未复现 rationale 章节的 high 问题 → 不误标已解决",
        )
        self.assert_eq(
            high_entry["last_seen_round"], 3,
            "跨章节调用不刷新其他章节条目的 last_seen_round",
        )

        # ---------- 断裂点1：critic 注入（exclude_resolved=True）----------
        # 重置为 2 条未解决
        opt._state = {"open_critical_issues": [
            {"severity": "critical", "section": "rationale", "description": "临界问题A",
             "first_seen_round": 1, "last_seen_round": 2, "round_resolved": None, "stale": False},
            {"severity": "high", "section": "content", "description": "高优先级问题B",
             "first_seen_round": 1, "last_seen_round": 2, "round_resolved": None, "stale": False},
            {"severity": "critical", "section": "scheme", "description": "已解决问题C",
             "first_seen_round": 1, "last_seen_round": 1, "round_resolved": 2, "stale": False},
        ]}
        critic_text = opt._build_p0_memory_text("p1", exclude_resolved=True)
        self.assert_in("临界问题A", critic_text, "critic 注入包含未解决 critical")
        self.assert_in("高优先级问题B", critic_text, "critic 注入包含未解决 high")
        self.assert_true(
            "已解决问题C" not in critic_text,
            "critic 注入不应包含已解决问题",
        )

        # ---------- 断裂点2：writer 注入（exclude_resolved=False）----------
        writer_text = opt._build_p0_memory_text("p1", exclude_resolved=False)
        self.assert_in("临界问题A", writer_text, "writer 注入包含未解决 critical")
        self.assert_in("已解决问题C", writer_text, "writer 注入包含最近已解决问题（防横跳）")

        # ---------- v7.2.56（#6 偏离修复）：critical 下限保护 ----------
        # 场景 A：critical 15 条 + high 10 条 → critical 全量注入（>12 不截断），
        # high 截断 12-15=0 条——旧平顶 [:12] 会丢 3 条 critical。
        crit_entries = [
            {"severity": "critical", "section": "rationale", "description": f"临界问题编号{i:02d}",
             "first_seen_round": 1, "last_seen_round": 2, "round_resolved": None, "stale": False}
            for i in range(15)
        ]
        high_entries = [
            {"severity": "high", "section": "content", "description": f"高优问题编号{i:02d}",
             "first_seen_round": 1, "last_seen_round": 2, "round_resolved": None, "stale": False}
            for i in range(10)
        ]
        opt._state = {"open_critical_issues": crit_entries + high_entries}
        text_a = opt._build_p0_memory_text("p1", exclude_resolved=True)
        self.assert_in("临界问题编号14", text_a,
                       "critical 超过 12 条时不得被平顶截断（下限保护）")
        self.assert_true(
            "高优问题编号00" not in text_a,
            "critical 已占满 12 水位时 non-critical 截断为 0 条",
        )

        # 场景 B：critical 5 条 + high 20 条 → non-critical 截断 12-5=7 条
        high20 = [
            {"severity": "high", "section": "content", "description": f"高优问题编号{i:02d}",
             "first_seen_round": 1, "last_seen_round": 2, "round_resolved": None, "stale": False}
            for i in range(20)
        ]
        opt._state = {"open_critical_issues": crit_entries[:5] + high20}
        text_b = opt._build_p0_memory_text("p1", exclude_resolved=True)
        n_high = sum(1 for i in range(20) if f"高优问题编号{i:02d}" in text_b)
        self.assert_eq(n_high, 7,
                       f"non-critical 应按 12-critical 条数截断（期望 7 实得 {n_high}）")
        self.assert_in("临界问题编号04", text_b, "critical 5 条全量注入")

        # 场景 C：存储上限 40 的 critical 优先——45 条（crit 8 + high 37）时
        # 旧排序（纯 last_seen）可能把 critical 挤出，新排序 critical 保底。
        bulk = crit_entries[:8] + [
            {"severity": "high", "section": "content", "description": f"近期高优{i:02d}",
             "first_seen_round": 1, "last_seen_round": 9, "round_resolved": None, "stale": False}
            for i in range(37)
        ]
        opt._state = {"open_critical_issues": []}
        merged5 = opt._update_open_critical_issues(
            "p1", [], current_round=9, focus_section_key="content")
        opt._state = {"open_critical_issues": bulk}
        # 直接验证排序函数行为：经 _update 合并后 critical 必须在保留集内
        merged6 = opt._update_open_critical_issues(
            "p1",
            [{"severity": "high", "line": "驱动合并的当轮问题"}],
            current_round=9, focus_section_key="content")
        crit_kept = sum(1 for e in merged6 if e.get("severity") == "critical")
        self.assert_eq(crit_kept, 8,
                       f"40 上限裁剪不得丢 critical（期望保留 8 实得 {crit_kept}）")
        self.assert_true(len(merged6) <= 40, "总条数仍受 40 上限约束")

        # ---------- 断裂点5：达标判定 P0 清零 ----------
        comp = self._comp
        # 5.1 5 模块全胜 + monitor 达标，但存在未解决 critical P0 → 不达标
        comp._state = {
            "status": "optimizing",
            "score_history": [{"score": 0.9}],
            "last_score": 0.9,
            "section_passes": {k: True for k in ["rationale", "content", "scheme", "full_review", "references", "method_manual"]},
            "optimization_rounds": 5,
            "monitor_history": [{"monitor_independent_score": 0.92}],
            "open_critical_issues": [
                {"severity": "critical", "section": "rationale", "description": "致命 P0",
                 "round_resolved": None, "stale": False},
            ],
        }
        threshold = {"min_overall_score": 0.80}
        res = comp._check_done("p1", threshold)
        self.assert_eq(res["done"], False, "存在未解决 critical P0 → 不予达标")
        self.assert_true("未解决" in res["reason"], "reason 说明存在未解决 critical P0")

        # 5.2 5 模块全胜 + 无 critical P0（只有 high）→ 达标
        # 本段只验证 P0 拦截语义，临时关闭 v7.3.42 的 A 提醒开关，
        # 保留旧的"全胜即达标"路径作为观测口径。
        import os
        _old_panel = os.environ.get("LINSAI_A_GATE_PANEL_PROMPT")
        os.environ["LINSAI_A_GATE_PANEL_PROMPT"] = "0"
        try:
            comp._state["open_critical_issues"] = [
                {"severity": "high", "section": "content", "description": "高优问题",
                 "round_resolved": None, "stale": False},
            ]
            res2 = comp._check_done("p1", threshold)
            self.assert_eq(res2["done"], True, "仅 high 未解决（非 critical）→ 达标")

            # 5.3 5 模块全胜 + critical 已解决 → 达标
            comp._state["open_critical_issues"] = [
                {"severity": "critical", "section": "scheme", "description": "已解决",
                 "round_resolved": 5, "stale": False},
            ]
            res3 = comp._check_done("p1", threshold)
            self.assert_eq(res3["done"], True, "critical 已解决 → 达标")

            # 5.4 5 模块全胜 + critical stale → 达标（stale 不再拦截）
            comp._state["open_critical_issues"] = [
                {"severity": "critical", "section": "scheme", "description": "陈旧",
                 "round_resolved": None, "stale": True},
            ]
            res4 = comp._check_done("p1", threshold)
            self.assert_eq(res4["done"], True, "critical 已降级 stale → 不拦截达标")
        finally:
            if _old_panel is None:
                os.environ.pop("LINSAI_A_GATE_PANEL_PROMPT", None)
            else:
                os.environ["LINSAI_A_GATE_PANEL_PROMPT"] = _old_panel

        # ---------- 断裂点4：section_focus 放宽（通过 prompt 文本验证间接覆盖）----------
        self.assert_true(
            "待解决" in writer_text or "处理" in writer_text,
            "writer 注入文本提示处理待解决 P0",
        )


if __name__ == "__main__":
    import time
    suite = CrossRoundP0MemoryTests()
    suite.setup()
    t0 = time.time()
    suite.run_tests()
    suite.teardown()
    suite.duration = time.time() - t0
    from test_runner import print_report
    print_report([suite])