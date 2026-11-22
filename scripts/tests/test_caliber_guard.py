"""
test_caliber_guard.py — 评分口径守卫回归测试（v7.3.33 / BUG-43）

背景（本轮健康检查第二层定位）：
    v7.3.0 引入手册就绪度轮（method_manual）后，score_history 里出现
    **三类互不可比的评分口径**：
      section_4d     —— rationale/content/scheme/full_review 的 4 维加权分
      references_2d  —— 引用审校（rigor/completeness 均值）
      manual_2d      —— 方法手册就绪度（readiness/rigor 均值）

    但三处消费点各写一份过滤口径，且**都只排除了 references**——
    v7.3.0 加手册轮时未同步这三个位置：

      ① health_sensor._detect_score_drop（health_sensor.py:96-102）
         末两条直接相减，无任何口径守卫 → 口径切换被误报为「伪分数污染」。
         实测 phonon 0.71→0.10、chiral 0.73→0.10 两条告警全部来自
         references_2d→manual_2d 切换，不是污染。

      ② web_routes_system.py:624-628（审核会话上下文）与 :1475-1478
         （课题总览）→ 手册分被当章节分展示，且硬编码标注「章节评审口径」。
         实测审核页显示 phonon 0.10 / chiral 0.10 / houston 0.82，
         而顶层 last_score 分别为 0.71 / 0.73 / 0.78。

      ③ lifecycle/utils.py:260 should_auto_rollback
         → 手册分被当章节分参与「连续下降 / 历史最佳」判定，
         实测 5 个在优化课题受影响（houston 3 条手册分 0.66/0.75/0.82）。

    修复：口径过滤统一到 lifecycle/constants.py 的唯一真相源
    （is_two_dim_caliber / filter_section_caliber），三处消费点改为复用。

测试覆盖：
    1. is_two_dim_caliber 口径判定（caliber 优先，focus_section 兜底）
    2. filter_section_caliber 过滤章节口径条目
    3. health_sensor 骤降检测：跨口径不误报 / 同口径仍检出
    4. should_auto_rollback：手册分不参与连续下降与历史最佳
    5. Web API 展示分取章节口径（与顶层 last_score 一致）
    6. 反向断言：复刻旧实现（只排 references）必然误报——确认测试非自证绿

注意：本测试不调用 hermes/LLM，不写生产目录。

用法示例：
    python3 scripts/tests/test_caliber_guard.py
"""

import sys

from test_runner import TestSuite, create_isolated_env


class CaliberGuardTests(TestSuite):
    def __init__(self):
        super().__init__("评分口径守卫回归测试")

    def run_tests(self):
        env = create_isolated_env()
        try:
            from lifecycle.constants import (
                CALIBER_MANUAL_2D,
                CALIBER_REFERENCES_2D,
                CALIBER_SECTION_4D,
                filter_section_caliber,
                is_two_dim_caliber,
            )
            from lifecycle.utils import should_auto_rollback
            from health_sensor import _detect_score_drop

            # ---------- 1. is_two_dim_caliber 口径判定 ----------
            self.assert_eq(
                is_two_dim_caliber({"caliber": CALIBER_SECTION_4D}),
                False, "section_4d 是章节口径，不算两维")
            self.assert_eq(
                is_two_dim_caliber({"caliber": CALIBER_REFERENCES_2D}),
                True, "references_2d 是两维专用口径")
            self.assert_eq(
                is_two_dim_caliber({"caliber": CALIBER_MANUAL_2D}),
                True, "manual_2d 是两维专用口径")
            # caliber 优先于 focus_section
            self.assert_eq(
                is_two_dim_caliber({"caliber": CALIBER_SECTION_4D,
                                    "focus_section": "method_manual"}),
                False, "caliber 字段优先于 focus_section")
            # 缺 caliber 时按 focus_section 兜底（历史条目兼容）
            self.assert_eq(
                is_two_dim_caliber({"focus_section": "references"}),
                True, "缺 caliber 时 references 按两维兜底")
            self.assert_eq(
                is_two_dim_caliber({"focus_section": "method_manual"}),
                True, "缺 caliber 时 method_manual 按两维兜底")
            self.assert_eq(
                is_two_dim_caliber({"focus_section": "rationale"}),
                False, "缺 caliber 时章节轮不算两维")

            # ---------- 2. filter_section_caliber ----------
            hist = [
                {"focus_section": "rationale", "score": 0.75,
                 "caliber": CALIBER_SECTION_4D},
                {"focus_section": "references", "score": 0.90,
                 "caliber": CALIBER_REFERENCES_2D},
                {"focus_section": "method_manual", "score": 0.95,
                 "caliber": CALIBER_MANUAL_2D},
                {"focus_section": "scheme", "score": 0.70,
                 "caliber": CALIBER_SECTION_4D},
            ]
            kept = filter_section_caliber(hist)
            self.assert_eq(
                len(kept), 2, "过滤后应只剩 2 条章节口径条目")
            self.assert_eq(
                [e["focus_section"] for e in kept], ["rationale", "scheme"],
                "过滤后应保留章节口径条目、剔除 references 与 method_manual")

            # ---------- 3. health_sensor 跨口径不误报 ----------
            cross = [
                {"round": 1, "score": 0.71, "caliber": CALIBER_REFERENCES_2D,
                 "focus_section": "references"},
                {"round": 1, "score": 0.10, "caliber": CALIBER_MANUAL_2D,
                 "focus_section": "method_manual"},
            ]
            self.assert_eq(
                _detect_score_drop(cross), None,
                "跨口径 references_2d→manual_2d 不应判为骤降")
            # 同口径真骤降仍须检出（守卫不得掩盖真信号）
            same = [
                {"round": 3, "score": 0.81, "caliber": CALIBER_SECTION_4D,
                 "focus_section": "rationale"},
                {"round": 4, "score": 0.18, "caliber": CALIBER_SECTION_4D,
                 "focus_section": "rationale"},
            ]
            d = _detect_score_drop(same)
            self.assert_true(d is not None, "同口径真骤降仍应检出")
            self.assert_eq(d["delta"] if d else None, 0.63, "同口径分差 0.63")

            # ---------- 4. should_auto_rollback 手册分不参与判定 ----------
            manual_mixed = [
                {"round": 1, "focus_section": "rationale", "score": 0.75},
                {"round": 1, "focus_section": "method_manual", "score": 0.95},
                {"round": 1, "focus_section": "scheme", "score": 0.70},
                {"round": 1, "focus_section": "full_review", "score": 0.62},
            ]
            plan = should_auto_rollback({"score_history": manual_mixed})
            self.assert_true(plan is not None, "混入手册高分不应阻断回退判定")
            self.assert_eq(
                plan["best_score"] if plan else None, 0.75,
                "历史最佳应取章节口径 0.75，而非手册 0.95")
            # 手册低分不得制造伪「连续下降」（章节分仅 2 条，不足 3 条门槛）
            manual_low = [
                {"round": 1, "focus_section": "rationale", "score": 0.80},
                {"round": 1, "focus_section": "method_manual", "score": 0.10},
                {"round": 1, "focus_section": "content", "score": 0.70},
            ]
            self.assert_eq(
                should_auto_rollback({"score_history": manual_low}), None,
                "手册低分（0.10）不应被当作章节分参与连续下降判定")

            # ---------- 5. Web API 展示分口径 ----------
            # 复刻 web_routes_system.py 的取分逻辑（排除两维口径后取最近一条）
            def api_score(history):
                for h in reversed(history):
                    if not is_two_dim_caliber(h):
                        return h.get("score")
                return None

            self.assert_eq(
                api_score(hist), 0.70,
                "展示分应取最近一条章节口径分（0.70），而非手册 0.95")
            self.assert_eq(
                api_score(cross), None,
                "全为两维口径时展示分应为空（不伪造章节分）")

            # ---------- 6. 反向断言：复刻旧实现必然误报 ----------
            def old_api_score(history):
                for h in reversed(history):
                    if h.get("focus_section") != "references":
                        return h.get("score")
                return None

            # 反向断言数据集：手册条目在最后（真实生产中手册轮是最新一轮）
            old_shape = [
                {"round": 1, "focus_section": "rationale", "score": 0.75,
                 "caliber": CALIBER_SECTION_4D},
                {"round": 1, "focus_section": "scheme", "score": 0.70,
                 "caliber": CALIBER_SECTION_4D},
                {"round": 1, "focus_section": "method_manual", "score": 0.95,
                 "caliber": CALIBER_MANUAL_2D},
            ]
            self.assert_eq(
                old_api_score(old_shape), 0.95,
                "旧实现（只排 references）会取到手册分 0.95——反例成立")
            self.assert_eq(
                api_score(old_shape), 0.70,
                "新实现取最近一条章节口径分 0.70——正例成立")
            self.assert_true(
                old_api_score(old_shape) != api_score(old_shape),
                "新旧实现必须给出相反结论，确保本测试不是自证绿")
            old_cross = [
                {"round": 1, "score": 0.71, "caliber": CALIBER_REFERENCES_2D,
                 "focus_section": "references"},
                {"round": 1, "score": 0.10, "caliber": CALIBER_MANUAL_2D,
                 "focus_section": "method_manual"},
            ]
            self.assert_true(
                _detect_score_drop.__doc__ is not None
                and "同口径" in _detect_score_drop.__doc__,
                "修复后骤降检测注释应记录口径守卫语义")
            self.assert_eq(
                old_api_score(old_cross), 0.10,
                "旧实现会把手册分当章节分展示——反例成立")

        finally:
            import shutil

            shutil.rmtree(env, ignore_errors=True)


if __name__ == "__main__":
    import time

    suite = CaliberGuardTests()
    suite.setup()
    t0 = time.time()
    suite.run_tests()
    suite.teardown()
    suite.duration = time.time() - t0
    from test_runner import print_report

    print_report([suite])
