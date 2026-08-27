#!/usr/bin/env python3
"""
test_mechanism_hardening.py — v6.9.28 对抗/自优化机制加固回归测试

覆盖三个修复点：
    1. 锚点绑定顺序修复（references 轮跳过 + 绑定移至专用计分之后）
       - references 评审不受锚点结论 cap（口径为 rigor/completeness）
       - 源码级顺序守卫：references 专用计分代码段必须先于锚点绑定段
    2. writer 顽固升级（连续两轮负分 + 表面修改评价 → 强制逐条响应块）
       - 触发：最近 2 条 history 均负 delta 且 reason 命中表面修改关键词
       - 不触发：单轮负分 / 无关键词 / history 不足 2 条
       - 触发后：枚举 critic 报告 critical/high 问题行；报告缺失时输出兜底要求
    3. prompt_optimizer 语义去重（v6.9.25 合并历史规则后防重复追加）
       - 改写措辞的同义建议（占位符规则 vs SOUL 运行纪律正文）→ 命中率 ≥0.6
       - 全新内容 → 命中率 <0.6，正常追加
       - _apply_suggestion 对同义建议跳过写入（文件不变、不备份）

背景：08-20 机制体检发现——moire R2/R3 writer 连续表面修改仅罚不改（修复率
1/7）；锚点绑定在 references 专用计分之前执行被覆盖；v6.9.25 手工合并
auto-opt 规则后 fingerprint 7 天窗口过期会重复追加同义规则。

注意：不调用 LLM，运行于隔离临时目录。

用法示例：
    python3 scripts/tests/test_mechanism_hardening.py
"""

import sys
import json
import shutil
import importlib
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT


def _load_optimize_module(tmp_root: Path):
    """在隔离目录下加载 proposal_lifecycle.optimize 并返回 OptimizeMixin。"""
    for mod_name in ["proposal_lifecycle.optimize", "proposal_lifecycle"]:
        if mod_name in sys.modules:
            del sys.modules[mod_name]
    importlib.import_module("proposal_lifecycle.optimize")
    import proposal_lifecycle as _pl
    _pl.PROJECT_ROOT = tmp_root
    from proposal_lifecycle.optimize import OptimizeMixin

    class _Fake(OptimizeMixin):
        def __init__(self):
            pass

    return _Fake()


class AnchorOrderTests(TestSuite):
    """1：锚点绑定顺序修复。"""

    def __init__(self):
        super().__init__("锚点绑定顺序修复测试（v6.9.28-1）")

    def setup(self):
        self.tmp_root = create_isolated_env()
        self._opt = _load_optimize_module(self.tmp_root)

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def run_tests(self):
        opt = self._opt

        # 1.1 references 口径不受锚点结论影响——专用计分独立于绑定函数。
        #     模拟 references 轮的实际数值流：rigor/completeness 平均。
        ref_dims = {"rigor": 0.58, "completeness": 0.66}
        ref_score = sum(ref_dims.values()) / len(ref_dims)
        self.assert_eq(round(ref_score, 2), 0.62, "references 专用计分 = (rigor+completeness)/2")

        # 1.2 差距明显结论若错误绑定 references 分（0.62 < 0.84）虽无实害，
        #     但口径错误；验证绑定函数对纯 references 维度无 expression 可 cap
        dims = {"rigor": 0.58, "completeness": 0.66}
        out = opt._apply_anchor_conclusion_binding(
            "p1", "锚点对比结论：差距明显", dims, ref_score, "general")
        self.assert_eq(dims["rigor"], 0.58, "绑定不应修改 rigor")
        self.assert_eq(out, ref_score, "无 expression 维度时绑定不应改综合分")

        # 1.3 源码级顺序守卫：references 专用计分段必须先于锚点绑定段出现
        #     （v6.9.28 前绑定在前者的赋值下被覆盖，references 轮形同虚设）
        src = Path(opt.__module__.replace(".", "/") + ".py")
        if not src.exists():
            src = Path(__file__).parent.parent / "proposal_lifecycle" / "optimize.py"
        text = src.read_text(encoding="utf-8")
        pos_ref = text.find("references 评审专用计分")
        pos_bind = text.find("锚点对比结论与评分档位强制绑定——范本锚点成为分数锚")
        self.assert_true(pos_ref > 0, "应存在 references 专用计分段")
        self.assert_true(pos_bind > 0, "应存在锚点绑定段")
        self.assert_true(
            pos_ref < pos_bind,
            "references 专用计分必须先于锚点绑定（防覆盖回归）",
        )
        # 1.4 references 轮跳过绑定的守卫注释存在（防误删）
        self.assert_true(
            "references 评审跳过绑定" in text,
            "references 轮跳过绑定的注释守卫应存在",
        )


class WriterEscalationTests(TestSuite):
    """2：writer 顽固升级机制。"""

    def __init__(self):
        super().__init__("writer 顽固升级测试（v6.9.28-2）")

    def setup(self):
        self.tmp_root = create_isolated_env()
        (self.tmp_root / "memory").mkdir(parents=True, exist_ok=True)
        (self.tmp_root / "05_review").mkdir(parents=True, exist_ok=True)
        self._opt = _load_optimize_module(self.tmp_root)
        self._report = self.tmp_root / "05_review" / "critic-round-3.md"
        self._report.write_text(
            "# 对抗评审报告（第3轮）\n"
            "### [critical] C1 — 编号 [12] 重复\n- 位置：references.md\n"
            "### [critical] C3 — [22] 作者署名错位\n- 位置：references.md\n"
            "### [high] H1 — [9] 标题拼写错误\n- 位置：references.md\n"
            "### [medium] M1 — 格式建议\n",
            encoding="utf-8")

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _write_scores(self, history):
        (self.tmp_root / "memory" / "agent-scores.json").write_text(
            json.dumps({"writer": {"score": 57.3, "history": history},
                        "critic": {"score": 97.0, "history": []}},
                       ensure_ascii=False),
            encoding="utf-8")

    def run_tests(self):
        opt = self._opt

        # 2.1 触发：连续两轮负分 + 表面修改评价 → 升级块含问题清单
        self._write_scores([
            {"delta": -16.9, "reason": "writer-r22 diff 仅 5 行，正文零改动", "at": "2026-08-20T04:19:52Z"},
            {"delta": -8.5, "reason": "writer 未修复 C3 critical 等问题", "at": "2026-08-20T14:21:54Z"},
        ])
        block = opt._build_writer_escalation_block(str(self._report))
        self.assert_true("顽固升级" in block, "触发时应输出顽固升级警告")
        self.assert_true("C1" in block and "C3" in block, "应枚举 critical 问题行")
        self.assert_true("H1" in block, "应枚举 high 问题行")
        self.assert_true("M1" not in block, "medium 问题不应枚举（聚焦 critical/high）")
        self.assert_true("问题→处理结果" in block, "应强制要求输出对照表")

        # 2.2 不触发：最近一轮 delta 为正
        self._write_scores([
            {"delta": -8.5, "reason": "未修复问题", "at": "2026-08-20T04:00:00Z"},
            {"delta": 4.4, "reason": "实质性参考文献工作", "at": "2026-08-20T14:00:00Z"},
        ])
        self.assert_eq(opt._build_writer_escalation_block(str(self._report)), "",
                       "最近一轮正分不应触发")

        # 2.3 不触发：负分但 reason 无表面修改关键词
        self._write_scores([
            {"delta": -3.0, "reason": "评分口径偏差", "at": "2026-08-20T04:00:00Z"},
            {"delta": -2.0, "reason": "格式问题", "at": "2026-08-20T14:00:00Z"},
        ])
        self.assert_eq(opt._build_writer_escalation_block(str(self._report)), "",
                       "无表面修改关键词不应触发")

        # 2.4 不触发：history 不足 2 条
        self._write_scores([{"delta": -10.0, "reason": "未修复 critical", "at": "2026-08-20T04:00:00Z"}])
        self.assert_eq(opt._build_writer_escalation_block(str(self._report)), "",
                       "history 不足 2 条不应触发")

        # 2.5 触发但报告缺失 → 兜底要求（无问题行但有对照表要求）
        self._write_scores([
            {"delta": -16.9, "reason": "零改动", "at": "2026-08-20T04:00:00Z"},
            {"delta": -8.5, "reason": "未处理 critic 问题", "at": "2026-08-20T14:00:00Z"},
        ])
        block2 = opt._build_writer_escalation_block(str(self.tmp_root / "nonexistent.md"))
        self.assert_true("顽固升级" in block2, "报告缺失也应触发升级警告")
        self.assert_true("问题→处理结果" in block2, "报告缺失也应要求对照表")
        self.assert_true("C1" not in block2, "报告缺失时不应有具体问题行")

        # 2.6 agent-scores.json 缺失 → 静默返回空
        (self.tmp_root / "memory" / "agent-scores.json").unlink()
        self.assert_eq(opt._build_writer_escalation_block(str(self._report)), "",
                       "agent-scores 缺失应返回空串")


class SemanticDedupTests(TestSuite):
    """3：prompt_optimizer 语义去重。"""

    SOUL_BODY = (
        "# Writer Profile\n\n## 运行纪律\n\n"
        "3. **禁止占位符**：不得提交\"待补充/TBD/待核验/XXX\"等占位内容；"
        "信息不足处改写为不依赖该信息的表述，或明确标注\"需要 researcher 补充文献\""
        "并给出替代论证。\n"
    )
    PARAPHRASED_RULE = (
        "\n<!--auto-opt:start:ps-x:2026-08-20T00:00:00Z:占位符|待.*核验|TBD-->\n"
        "## 自动优化规则（评分分析 2 次证据）\n\n"
        "提交前全文检索'待补充/TBD/待核验/XXX'，命中处一律改写为不依赖该信息的"
        "完整表述，或标注'需要 researcher 补充'并给出替代论证。\n"
        "<!--auto-opt:end:ps-x-->\n"
    )
    NEW_RULE = (
        "\n## 自动优化规则\n\n"
        "每张表格必须有表题，表题编号与正文引用一致，禁止无题表格。\n"
    )

    def __init__(self):
        super().__init__("语义去重测试（v6.9.28-3）")

    def setup(self):
        self.tmp_root = create_isolated_env()
        (self.tmp_root / "memory").mkdir(parents=True, exist_ok=True)
        (self.tmp_root / ".hermes" / "profiles" / "writer").mkdir(parents=True, exist_ok=True)
        self._soul = self.tmp_root / ".hermes" / "profiles" / "writer" / "SOUL.md"
        self._soul.write_text(self.SOUL_BODY, encoding="utf-8")

        for mod_name in ["prompt_optimizer"]:
            if mod_name in sys.modules:
                del sys.modules[mod_name]
        self.po = importlib.import_module("prompt_optimizer")
        patch_module_root("prompt_optimizer", self.tmp_root)

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def run_tests(self):
        po = self.po

        # 3.1 同义改写 → 命中率 ≥0.6
        ratio = po._semantic_overlap_ratio(self.PARAPHRASED_RULE.strip(), self.SOUL_BODY)
        self.assert_true(ratio >= 0.6,
                         f"同义规则命中率应 ≥0.6，实际 {ratio:.0%}")

        # 3.2 全新内容 → 命中率 <0.6
        ratio2 = po._semantic_overlap_ratio(self.NEW_RULE.strip(), self.SOUL_BODY)
        self.assert_true(ratio2 < 0.6,
                         f"全新规则命中率应 <0.6，实际 {ratio2:.0%}")

        # 3.3 完全相同 → 1.0（精确匹配路径之上仍兼容）
        ratio3 = po._semantic_overlap_ratio(self.SOUL_BODY, self.SOUL_BODY)
        self.assert_eq(ratio3, 1.0, "完全相同内容命中率为 1.0")

        # 3.4 _apply_suggestion：同义建议跳过写入（文件不变）
        suggestion = {
            "target_file": str(self._soul),
            "target_profile": "writer",
            "content": self.PARAPHRASED_RULE,
        }
        before = self._soul.read_text(encoding="utf-8")
        ok = po._apply_suggestion(suggestion)
        after = self._soul.read_text(encoding="utf-8")
        self.assert_true(ok, "同义建议应返回 True（视为已应用）")
        self.assert_eq(after, before, "同义建议不应写入文件")
        self.assert_true(
            "semantically_present" in str(suggestion.get("apply_note", "")),
            "应记录 semantically_present 注记",
        )

        # 3.5 _apply_suggestion：全新内容正常追加
        suggestion2 = {
            "target_file": str(self._soul),
            "target_profile": "writer",
            "content": self.NEW_RULE,
        }
        ok2 = po._apply_suggestion(suggestion2)
        after2 = self._soul.read_text(encoding="utf-8")
        self.assert_true(ok2, "全新建议应成功应用")
        self.assert_true("表题编号与正文引用一致" in after2, "全新建议应写入文件")


class ExecutorPathTests(TestSuite):
    """4：executor.py 线上路径机制守护（v6.9.30）。

    背景：v6.9.28 的锚点绑定/AI 检测修复只落在 optimize.py（微调度器
    未调用的死代码），线上实际执行路径 executor.py 缺失，导致
    'template=score anchor' 机制整体失效。本套件做源码级守卫，
    防止移植逻辑再次只修死代码。
    """

    def __init__(self):
        super().__init__("executor 线上路径机制守护测试（v6.9.30-4）")

    def setup(self):
        self.tmp_root = create_isolated_env()
        self._exec = Path(__file__).parent.parent / "lifecycle" / "executor.py"
        self._text = self._exec.read_text(encoding="utf-8")
        self._opt_src = Path(__file__).parent.parent / "proposal_lifecycle" / "optimize.py"
        self._opt_text = self._opt_src.read_text(encoding="utf-8")

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def run_tests(self):
        text = self._text

        # 4.1 critic 步骤必须先运行程序化 AI 检测（产出表达天花板）
        pos_critic_ai = text.find("def _run_critic_step")
        pos_ai_detect = text.find("ai_check = self._detect_ai_patterns")
        self.assert_true(pos_critic_ai > 0, "应存在 _run_critic_step")
        self.assert_true(pos_ai_detect > 0, "应存在 AI 检测调用")
        self.assert_true(
            pos_critic_ai < pos_ai_detect,
            "AI 检测应位于 _run_critic_step 内（critic 之前）",
        )

        # 4.2 AI 检测结果必须传入 critic（ai_check_result 参数）
        self.assert_true(
            "ai_check_result=ai_check" in text,
            "critic 调用应传入 ai_check_result",
        )

        # 4.3 writer 步骤必须应用锚点绑定（references 轮跳过）
        self.assert_true(
            "self._apply_anchor_conclusion_binding" in text,
            "writer 步骤应调用锚点绑定",
        )
        pos_ref_score = text.find("references 评审专用计分")
        pos_bind = text.find("锚点对比结论与评分档位强制绑定")
        self.assert_true(pos_ref_score > 0, "executor 应存在 references 专用计分段")
        self.assert_true(pos_bind > 0, "executor 应存在锚点绑定段")
        self.assert_true(
            pos_ref_score < pos_bind,
            "executor 中 references 专用计分必须先于锚点绑定（防覆盖回归）",
        )
        self.assert_true(
            'if section_key != "references":' in text,
            "executor 应存在 references 轮跳过绑定的守卫",
        )

        # 4.4 score_history 必须记录 ai_ceiling / ai_top_issues / anchor_conclusion
        self.assert_true('"ai_ceiling"' in text, "score_history 应含 ai_ceiling")
        self.assert_true('"ai_top_issues"' in text, "score_history 应含 ai_top_issues")
        self.assert_true('"anchor_conclusion"' in text, "score_history 应含 anchor_conclusion")

        # 4.5 程序化天花板强制执行（表达分 + 综合分 cap）
        self.assert_true(
            "dim_scores[\"expression\"] = ceiling" in text,
            "executor 应强制表达分 cap 至 AI 天花板",
        )
        self.assert_true(
            "overall_ceiling" in text,
            "executor 应存在综合分天花板",
        )

        # 4.6 references 评审超时 cap 必须 ≥1200s（v6.9.31）
        #     背景：references 输入含 references.md + 三个正文章节（约 106KB），
        #     MiniMax 慢 API 下主 critic 单章都要 1155s——600s cap 导致
        #     order-parameter r7 references-critic 连续 3 次超时卡死。
        opt_text = self._opt_text
        self.assert_true(
            "min(timeout, 1200)" in opt_text,
            "references 评审超时 cap 应为 1200s（v6.9.31 修复）",
        )
        self.assert_true(
            "min(timeout, 600)" not in opt_text,
            "references 评审不应再被 600s cap 限制",
        )

        # 4.7 writer 后程序化复检闭环（v6.9.33）
        #     背景：writer prompt 已注入 top_issues 明细但执行不力（moire 案例
        #     只修 1/7 问题）。复检用确定性检测验证 writer 是否实质修复表达：
        #     未达标（<0.85）必须严格提升，已达标只要求不显著倒退，references 跳过。
        self.assert_true(
            "ai_check_after = self._detect_ai_patterns" in text,
            "writer 后应二次运行 AI 检测（复检）",
        )
        self.assert_true(
            "expression_improved" in text,
            "应存在 expression_improved 判定",
        )
        self.assert_true(
            "and expression_improved" in text,
            "section_passed 应包含表达提升条件",
        )
        self.assert_true(
            '"ai_ceiling_after"' in text,
            "score_history 应含 ai_ceiling_after",
        )
        self.assert_true(
            'if section_key != "references" and ai_check:' in text,
            "references 轮应跳过表达复检",
        )


class WeeklyResetAnchorTests(TestSuite):
    """5：v6.9.38 跨周重置自然周锚点修复。

    背景：旧实现 delta_days = (now - last_fin).days < 6 的滚动 144h 时差
    判定，上周完成时刻晚于本周入口 cron 时刻时（08-16 11:51 完成 vs
    08-22 09:00 入口，时差 5 天 21 小时），入口 cron 必然差不满 6 天而
    no-op 却标记成功，依赖 6h repair 兜底，实测空转 3 小时。
    """

    def __init__(self):
        super().__init__("跨周重置自然周锚点测试（v6.9.38-5）")

    def setup(self):
        import tempfile
        self.tmp = Path(tempfile.mkdtemp())
        import weekend_pipeline.pipeline as pl
        self._pl = pl
        self._orig_datetime = pl.datetime

    def teardown(self):
        pl = self._pl
        pl.datetime = self._orig_datetime
        if self.tmp and self.tmp.exists():
            shutil.rmtree(self.tmp, ignore_errors=True)

    def _make_pipeline(self, finished_at):
        from weekend_pipeline.pipeline import WeekendPipeline
        p = WeekendPipeline.__new__(WeekendPipeline)
        p.state_path = self.tmp / "state.json"
        p.state = {"jobs": [{
            "job_id": "t1", "stage": "input", "status": "done",
            "finished_at": finished_at, "started_at": "x",
            "last_error": "e", "attempts": 2, "result": {"ok": 1},
        }]}
        return p

    def _freeze_now(self, y, m, d, hour, minute=0):
        """把 pipeline.datetime.now 冻结到指定本地时刻（Asia/Shanghai +8）。"""
        from datetime import datetime, timezone, timedelta as td
        tz8 = td(hours=8)

        class FakeDT(datetime):
            _frozen = datetime(y, m, d, hour, minute, 0, tzinfo=timezone.utc) - tz8

            @classmethod
            def now(cls, tz=None):
                return cls._frozen.astimezone() if tz is None else cls._frozen.astimezone(tz)
        self._pl.datetime = FakeDT

    def run_tests(self):
        # 源码路径锚定测试文件自身（cwd 可能是仓库根或 scripts/）
        _src_root = Path(__file__).parent.parent.parent

        # 5.1 修复主场景：上周六 11:51 完成（本地）→ 本周六 09:00 入口。
        #     旧滚动口径时差 5d21h（.days=5）不重置；新锚点口径
        #     anchor=本周六 00:00 > last_fin → 立即重置。
        self._freeze_now(2026, 8, 22, 9, 0)  # 周六 09:00 本地
        p = self._make_pipeline("2026-08-16T03:51:56Z")  # 08-16 11:51 本地
        n = p._reset_stage_for_new_week("input")
        self.assert_eq(n, 1, "上周完成早于本周六锚点应重置（修复主场景）")
        j = p.state["jobs"][0]
        self.assert_eq(j["status"], "pending", "重置后状态应为 pending")
        self.assert_eq(j["attempts"], 0, "重置后 attempts 应清零")
        self.assert_true("result" not in j, "重置后 result 应清除")

        # 5.2 边界保护：本周末内刚完成的 job 不被重置
        self._freeze_now(2026, 8, 22, 12, 0)  # 周六 12:00 本地
        p = self._make_pipeline("2026-08-22T00:30:00Z")  # 周六 08:30 本地
        n = p._reset_stage_for_new_week("input")
        self.assert_eq(n, 0, "本周末内完成不应重置")

        # 5.3 时间戳解析失败 → 安全不重置（不抛异常）
        p = self._make_pipeline("not-a-timestamp")
        n = p._reset_stage_for_new_week("input")
        self.assert_eq(n, 0, "时间戳异常应安全返回 0")

        # 5.4 源码级守卫：不应再有滚动 6 天判断
        src = (_src_root / "scripts/weekend_pipeline/pipeline.py").read_text(encoding="utf-8")
        self.assert_true(
            "if delta_days < 6" not in src,
            "旧的滚动 144h 判断应已移除",
        )


class TaskSyncRollbackTests(TestSuite):
    """6：v6.9.38 任务同步 completed→active 回退分支。

    背景：审核退回归零轮次重开后，映射命中的旧任务已标 completed 并移入
    completed/ 目录，同步代码只处理 backlog→active，任务面板与实际 job
    进度永久脱节（key-transient r1 job 6/25 但任务 completed）。
    """

    def __init__(self):
        super().__init__("任务同步回退分支测试（v6.9.38-6）")

    def setup(self):
        pass

    def teardown(self):
        pass

    def run_tests(self):
        _src_root = Path(__file__).parent.parent.parent
        src = (_src_root / "scripts/lifecycle/micro_scheduler.py").read_text(encoding="utf-8")

        # 6.1 completed→active 分支存在
        self.assert_true(
            'not round_complete and task.get("status") == "completed"' in src,
            "应存在 completed 且轮次未完成的判定分支",
        )
        # 6.2 分支内实际调用 transition 拉回 active
        idx = src.find('not round_complete and task.get("status") == "completed"')
        seg = src[idx:idx + 600]
        self.assert_true(
            'transition_task(existing_task_id, "active")' in seg,
            "completed 任务应被 transition 回 active",
        )

        # 6.3 状态机守卫：task_manager 允许 completed→active
        tm_src = (_src_root / "scripts/task_manager.py").read_text(encoding="utf-8")
        self.assert_true(
            '"completed": {"active", "backlog"}' in tm_src,
            "task_manager 状态机应允许 completed→active",
        )


class KbDistillAutoTests(TestSuite):
    """7：v6.9.38 KB 蒸馏自适应批量 + 告警口径统一。

    背景：日蒸馏 5 篇追不上日增 40+ 的进料（08-22 积压 347 连续 46 次
    告警不收敛）；health_sensor 与 kb_distill 口径不一致（347 vs 229），
    积压治理无法对账。
    """

    def __init__(self):
        super().__init__("KB 蒸馏自适应批量测试（v6.9.38-7）")

    def setup(self):
        pass

    def teardown(self):
        pass

    def run_tests(self):
        import sys as _sys
        _src_root = Path(__file__).parent.parent.parent
        _sys.path.insert(0, str(_src_root / "scripts"))
        from kb_distill import auto_batch_size

        # 7.1 档位边界
        self.assert_eq(auto_batch_size(347), 20, "积压 347 → 追赶档 20")
        self.assert_eq(auto_batch_size(301), 20, "积压 301 → 追赶档 20")
        self.assert_eq(auto_batch_size(300), 10, "积压 300（未超线）→ 消化档 10")
        self.assert_eq(auto_batch_size(151), 10, "积压 151 → 消化档 10")
        self.assert_eq(auto_batch_size(150), 5, "积压 150（未超线）→ 维持档 5")
        self.assert_eq(auto_batch_size(0), 5, "零积压 → 维持档 5")

        # 7.2 CLI 有 --auto 参数
        kd_src = (_src_root / "scripts/kb_distill.py").read_text(encoding="utf-8")
        self.assert_true('"--auto"' in kd_src, "kb_distill CLI 应有 --auto")

        # 7.3 cron wrapper 已改用 --auto（源码级）
        ctl_src = (_src_root / "scripts/lifecycle/controller.py").read_text(encoding="utf-8")
        self.assert_true(
            "kb_distill.py --auto" in ctl_src,
            "cron wrapper 应调用 --auto",
        )
        self.assert_true(
            "kb_distill.py --batch 5" not in ctl_src,
            "旧的固定 --batch 5 应移除",
        )

        # 7.4 kb_health 口径统一：调用 kb_distill.pending_distill_list
        kh_src = (_src_root / "scripts/kb_health.py").read_text(encoding="utf-8")
        self.assert_true(
            "from kb_distill import pending_distill_list" in kh_src,
            "kb_health 应调用蒸馏器同源清单函数",
        )


class NamingGuardTests(TestSuite):
    """8：v6.9.39 课题名称段字母开头守卫。

    背景：register_from_idea 从标题 ASCII 过滤提取 name，未保证命名规则
    要求的"名称段以字母开头"（[a-z][a-z0-9-]{1,40}）。标题含数字编号/
    波长时 name 以数字开头（08-22 实测 "322-frogcrab"），拼出的
    proposal_id 必被 validate_proposal_id 拒绝，注册静默失败且周末
    compose 的 job 整体仍标 success——new 配额空转需人工兜底（bc190e1
    手动补注册）。修复：name 定型前剥离前导数字段，空则回退占位名。
    """

    def __init__(self):
        super().__init__("课题名称段字母开头守卫测试（v6.9.39-8）")

    def setup(self):
        self.tmp_root = create_isolated_env()
        for stage in ["drafts", "optimizing", "pending_review", "archived"]:
            (self.tmp_root / "research_proposals" / stage).mkdir(parents=True, exist_ok=True)
        standards_src = REAL_ROOT / "memory" / "nsfc-standards.json"
        if standards_src.exists():
            (self.tmp_root / "memory").mkdir(parents=True, exist_ok=True)
            shutil.copy(standards_src, self.tmp_root / "memory" / "nsfc-standards.json")
        for mod_name in list(sys.modules.keys()):
            if mod_name.startswith("proposal_lifecycle") or mod_name == "idea_generator":
                del sys.modules[mod_name]
        import paths
        self._orig_project_root = paths.PROJECT_ROOT
        paths.PROJECT_ROOT = self.tmp_root
        import proposal_lifecycle.constants as plc
        self._orig_plc_root = plc.PROJECT_ROOT
        self._orig_plc_proposals = plc.PROPOSALS_ROOT
        plc.PROJECT_ROOT = self.tmp_root
        plc.PROPOSALS_ROOT = self.tmp_root / "research_proposals"
        patch_module_root("proposal_lifecycle", self.tmp_root)

    def teardown(self):
        import proposal_lifecycle.constants as plc
        plc.PROJECT_ROOT = self._orig_plc_root
        plc.PROPOSALS_ROOT = self._orig_plc_proposals
        import paths
        paths.PROJECT_ROOT = self._orig_project_root
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _idea(self, title, keywords=None):
        return {
            "title": title,
            "background": "测试背景",
            "gap": "测试缺口",
            "content": [],
            "approach": "x",
            "innovations": ["y"],
            "sources": [],
            "keywords": keywords or [],
            "generated_at": "2026-08-22T00:00:00Z",
        }

    def run_tests(self):
        import re as _re
        from proposal_lifecycle import ProposalLifecycle
        lc = ProposalLifecycle()

        # 8.1 主场景（08-22 实测复现）：标题数字开头 → 剥离后注册成功
        result = lc.register_from_idea(
            self._idea("322-frogcrab 阿秒条纹技术", ["attosecond", "streaking"]),
            project_type="general",
        )
        self.assert_true(
            result.get("success"),
            f"数字开头标题应注册成功而非被校验拒绝: {result.get('error', '')}",
        )
        pid = result.get("proposal_id", "")
        self.assert_true(
            not _re.match(r"^(general|key|major)-[0-9]", pid),
            f"ID 名称段不应以数字开头: {pid}",
        )
        v = lc.validate_proposal_id(pid)
        self.assert_true(v["valid"], f"剥离后的 ID 应通过命名校验: {pid}")

        # 8.2 纯中文标题 → keywords 回退链 → 回退词数字开头同样剥离
        result2 = lc.register_from_idea(
            self._idea("阿秒条纹技术", ["322-nm", "attosecond"]),
            project_type="general",
        )
        self.assert_true(
            result2.get("success"),
            f"中文标题走 keywords 回退应注册成功: {result2.get('error', '')}",
        )
        pid2 = result2.get("proposal_id", "")
        self.assert_true(
            not _re.match(r"^(general|key|major)-[0-9]", pid2),
            f"keywords 数字开头同样应被剥离: {pid2}",
        )

        # 8.2b 纯数字标题 → 剥离后为空 → 回退占位名
        result2b = lc.register_from_idea(
            self._idea("322", []),
            project_type="general",
        )
        self.assert_true(result2b.get("success"), f"纯数字标题应回退占位名注册成功: {result2b.get('error', '')}")

        # 8.3 正常字母开头标题不受影响
        result3 = lc.register_from_idea(
            self._idea("attosecond streaking camera", ["attosecond"]),
            project_type="general",
        )
        self.assert_true(result3.get("success"), "正常标题注册不受守卫影响")

        # 8.4 idea_generator 两处同模式守卫（源码级，防未来调用方踩坑）
        _src_root = Path(__file__).parent.parent.parent
        ig_src = (_src_root / "scripts" / "idea_generator.py").read_text(encoding="utf-8")
        self.assert_eq(
            ig_src.count('re.sub(r"^[0-9-]+", "", name)'),
            2,
            "_generate_proposal_id 与 dry_run 分支均应有前导数字剥离",
        )
        reg_src = (_src_root / "scripts" / "proposal_lifecycle" / "registration.py").read_text(encoding="utf-8")
        self.assert_true(
            're.sub(r"^[0-9-]+", "", name)' in reg_src,
            "register_from_idea 应有前导数字剥离",
        )


class ReferencesPreflightTests(TestSuite):
    """8：v6.9.42 references 程序化预检（任务重排核心）。

    背景：references critic 被要求读 references.md（40KB，60% 是工作日志）
    + 三个正文章节（62KB）≈ 106KB 找编号匹配——程序化可完成的任务交给
    LLM 导致连续超时（bsv/order-param 卡死）。预检以正则完成编号一致性，
    critic 只读 references.md + 预检表。
    """

    def __init__(self):
        super().__init__("references 预检测试（v6.9.42-8）")

    def setup(self):
        import tempfile
        self.tmp = Path(tempfile.mkdtemp())
        sec = self.tmp / "04_proposal" / "sections"
        sec.mkdir(parents=True)

    def teardown(self):
        if self.tmp and self.tmp.exists():
            shutil.rmtree(self.tmp, ignore_errors=True)
        # v6.9.54 现场还原：_load() 会 del + 重导入
        # proposal_lifecycle.optimize——重导入时其模块级常量从当时的
        # patch 根派生。跑完不清理会留给后续套件一个绑定旧根的模块
        # 对象（实测污染 test_optimize_v6817：standards_path 指向本
        # 套件根，relative_to 抛 ValueError 崩套件）。
        sys.modules.pop("proposal_lifecycle.optimize", None)

    def _load(self):
        import importlib
        for mod_name in list(sys.modules):
            if mod_name == "proposal_lifecycle.optimize":
                del sys.modules[mod_name]
        importlib.import_module("proposal_lifecycle.optimize")
        from proposal_lifecycle.optimize import _references_preflight
        return _references_preflight

    def run_tests(self):
        preflight = self._load()
        sec = self.tmp / "04_proposal" / "sections"

        # 8.1 编号一致性核心：缺失/未引用识别（粗体体例）
        (sec / "rationale.md").write_text("论断A[1] 论断B[3] 论断C[critical] 无害", encoding="utf-8")
        (sec / "content.md").write_text("论断D[2]", encoding="utf-8")
        (sec / "scheme.md").write_text("论断E[5]", encoding="utf-8")
        (sec / "references.md").write_text(
            "## 参考文献\n\n**[1]** A. x.\n\n**[2]** B. y.\n\n**[3]** C. z.\n\n**[4]** D. w.\n",
            encoding="utf-8")
        out = preflight(self.tmp)
        self.assert_true("[5]" in out.split("正文引用但列表缺失")[1].split("\n")[0],
                         "正文引用 [5] 但列表缺失应被识别")
        self.assert_true("[4]" in out, "列表 [4] 未被正文引用应被识别")
        self.assert_true("4 条" in out, "粗体体例 **[N]** 应被正确计数")
        self.assert_true("[critical]" not in out or "正文引用标记：3" in out,
                         "英文标签 [critical] 不应计入引用编号")

        # 8.2 行首体例兼容
        (sec / "references.md").write_text("[1] A. x.\n[2] B. y.\n", encoding="utf-8")
        out2 = preflight(self.tmp)
        self.assert_true("2 条" in out2, "行首体例 [N] 应被识别")

        # 8.3 膨胀告警（>25KB）
        big = "## 参考文献\n\n" + "**[1]** A. padding. " + "x" * 30000 + "\n"
        (sec / "references.md").write_text(big, encoding="utf-8")
        out3 = preflight(self.tmp)
        self.assert_true("膨胀告警" in out3, ">25KB 应触发膨胀告警")
        self.assert_true("05_review" in out3, "告警应建议工作日志迁往 05_review")

        # 8.4 引用数量对标
        (sec / "references.md").write_text(
            "\n".join(f"**[{i}]** Ref {i}." for i in range(1, 51)), encoding="utf-8")
        out4 = preflight(self.tmp)
        self.assert_true("超出区间" in out4, ">40 篇应标记超出区间")

        # 8.5 源码级守卫：prompt 不再读正文章节、含预检注入
        src = Path(__file__).parent.parent / "proposal_lifecycle" / "optimize.py"
        text = src.read_text(encoding="utf-8")
        self.assert_true(
            "_references_preflight(prop_dir)" in text,
            "critic prompt 应调用预检函数",
        )
        idx = text.find("程序化预检结果")
        seg = text[max(0, idx - 3000):idx]
        self.assert_true(
            "body_files" not in seg,
            "references 分支不应再构建正文文件列表（旧超载输入）",
        )
        self.assert_true(
            "编号一致性已由预检完成" in text,
            "prompt 应声明编号一致性已程序化完成",
        )

        # 8.6 来源校验（v6.9.57）：未命中条目入优先核查清单、命中条目不误报
        from proposal_lifecycle.optimize import _reference_source_preflight
        (sec / "references.md").write_text(
            "**[1]** Known Author. Verified title. DOI: 10.1234/known\n"
            "**[2]** Ghost Author. Suspect title. DOI: 10.9999/ghost\n"
            "**[3]** Plain entry without any identifier\n",
            encoding="utf-8")
        (self.tmp / "02_literature").mkdir(exist_ok=True)
        (self.tmp / "02_literature" / "notes.md").write_text(
            "10.1234/known | Verified title | 检索命中", encoding="utf-8")
        out5 = _reference_source_preflight(self.tmp, (sec / "references.md").read_text(encoding="utf-8"))
        warn_lines = [ln for ln in out5 if "优先核查" in ln or "未在本课题检索产物" in ln]
        no_id_lines = [ln for ln in out5 if "无标识符" in ln]
        self.assert_true(any("[2]" in ln for ln in warn_lines),
                         "池外条目 [2] 应进优先核查清单")
        self.assert_true(
            not any("[1]" in ln for ln in warn_lines),
            "池内条目 [1] 不应出现在未命中清单")
        self.assert_true(any("[3]" in ln for ln in no_id_lines),
                         "无 ID 条目 [3] 应单独归类为无标识符")

        # 8.6b（v6.9.59 回归）：ID 归一化抗污染——全角标点后缀/markdown
        # 加粗/行尾句点不得产生复合污染 ID 或漏提取（7 课题实测 9 条误杀
        # 形态："DOI: 10.1364/OPTICA.510789；arXiv:2302.04127."）。
        from proposal_lifecycle.optimize import _collect_reference_ids
        self.assert_eq(
            _collect_reference_ids("DOI: 10.1364/OPTICA.510789；arXiv:2302.04127."),
            {"10.1364/optica.510789", "2302.04127"},
            "全角分号应截断 DOI，行尾句点不应吞入/漏掉 arXiv ID")
        self.assert_eq(
            _collect_reference_ids("参见 10.1088/0256-307x/43/2/020401** 已验证"),
            {"10.1088/0256-307x/43/2/020401"},
            "markdown 加粗尾缀 ** 不应污染 DOI")
        self.assert_eq(
            _collect_reference_ids("10.1038/s41566-025-01802-1，另见 2401.12345"),
            {"10.1038/s41566-025-01802-1", "2401.12345"},
            "全角逗号应截断 DOI 并独立提取相邻 arXiv ID")

        # 8.7 池空时跳过（课题早期不误报）——需临时隔离真实知识库根
        import proposal_lifecycle.optimize as _opt
        empty_tmp = self.tmp / "empty_case"
        (empty_tmp / "04_proposal" / "sections").mkdir(parents=True, exist_ok=True)
        _orig_root = _opt._pl.PROJECT_ROOT
        _opt._pl.PROJECT_ROOT = empty_tmp
        try:
            out6 = _reference_source_preflight(empty_tmp, "[1] Some Ref. DOI: 10.1/x")
        finally:
            _opt._pl.PROJECT_ROOT = _orig_root
        self.assert_true(
            any("跳过" in ln for ln in out6) or out6 == [],
            "检索池与知识库均空时应跳过来源校验")


class MetricsPreflightTests(TestSuite):
    """9：v6.9.46 跨章节指标一致性预检 + writer 输入对齐 + 纯净性红线。

    背景：full_review critic 读全部 5 章节（最大 180KB）找数字矛盾——
    程序化可完成的指标比对交给 LLM（同构于 references 问题）。writer
    无条件列出全部章节文件供读但指令只改聚焦章节；且 writer 是
    references.md 工作日志污染的源头。
    """

    def __init__(self):
        super().__init__("指标预检与 writer 对齐测试（v6.9.46-9）")

    def setup(self):
        import tempfile
        self.tmp = Path(tempfile.mkdtemp())
        sec = self.tmp / "04_proposal" / "sections"
        sec.mkdir(parents=True)

    def teardown(self):
        if self.tmp and self.tmp.exists():
            shutil.rmtree(self.tmp, ignore_errors=True)

    def run_tests(self):
        import importlib
        for mod_name in list(sys.modules):
            if mod_name == "proposal_lifecycle.optimize":
                del sys.modules[mod_name]
        importlib.import_module("proposal_lifecycle.optimize")
        from proposal_lifecycle.optimize import _cross_section_metrics_preflight
        sec = self.tmp / "04_proposal" / "sections"

        # 9.1 一致指标识别 + 差异项检出
        (sec / "rationale.md").write_text("强度 0.5-2 TW/cm²，脉宽 30 fs，温度 300 K", encoding="utf-8")
        (sec / "content.md").write_text("驱动 0.5-2 TW/cm²，30 fs 脉冲", encoding="utf-8")
        (sec / "scheme.md").write_text("光强 0.5-2 TW/cm²，脉宽 28 fs（收紧）", encoding="utf-8")
        out = _cross_section_metrics_preflight(self.tmp)
        self.assert_true("强度 TW/cm²=0.5" in out or "峰值强度 TW/cm²" in out,
                         "跨章节一致的强度指标应被识别")
        self.assert_true("时间 fs" in out and "差异" in out,
                         "30 vs 28 fs 差异应被标记")

        # 9.2 无差异时不误报
        (sec / "scheme.md").write_text("光强 0.5-2 TW/cm²，脉宽 30 fs", encoding="utf-8")
        out2 = _cross_section_metrics_preflight(self.tmp)
        self.assert_true("无数值集差异项" in out2, "全一致时应报告无差异")

        # 9.3 源码守卫：full_review critic 排除 references + 附预检
        # v6.9.53 起 references 与 full_review 一并排除（骨架是派生索引），
        # 守卫同步更新为成员检查写法，语义不放松。
        src = (Path(__file__).parent.parent / "proposal_lifecycle" / "optimize.py").read_text(encoding="utf-8")
        self.assert_true(
            "and s['key'] not in (\"references\", \"full_review\")" in src,
            "full_review critic 文件列表应排除 references.md 与 full_review.md",
        )
        self.assert_true(
            "_cross_section_metrics_preflight(prop_dir)" in src,
            "full_review critic 应附指标预检",
        )

        # 9.4 writer 输入对齐：章节级无跨章节 P0 只列聚焦章节
        self.assert_true(
            "writer_read_files" in src,
            "writer 应使用对齐后的读取列表变量",
        )
        self.assert_true(
            "if focus_section and not _allow_cross:" in src,
            "章节级且无跨章节 P0 时应只列聚焦章节",
        )

        # 9.5 纯净性红线：禁止工作日志进章节文件
        self.assert_true(
            "文件纯净性红线" in src,
            "writer prompt 应含文件纯净性红线",
        )
        self.assert_true(
            "严禁写入任何工作过程记录" in src,
            "应明确禁止核校日志进章节文件",
        )
        self.assert_true(
            "迁移至 05_review" in src,
            "应要求迁移既有污染内容",
        )


class AICeilingFairnessTests(TestSuite):
    """10：v6.9.47 AI 天花板公平性修复（白名单/千字归一/raw 比较/章节归因）。

    背景：attosecond 课题 AI 天花板连续 5 轮卡死 0.50，writer 被判定
    "未实质修复表达问题"。逐项核查发现四层叠加缺陷：① '关键科学问题'×5
    （NSFC 法定章节）、'系统误差'（物理术语）、'有效性'（validity）、
    '同时电离'（物理概念）等不可删词被裸词计数误伤——修复指令物理上
    不可执行；② 绝对阈值 12 次对 14K 字长文意味着 0.86 次/千字，中文
    科研写作正常密度 2-4 次/千字，达标不可能；③ 复检比较 floor(0.5)
    之后的值，0.6→0.5 的实质改善被掩埋成 0.50→0.50；④ writer 每轮
    只修聚焦章节，但复检用三章节合并口径，单章节完美修复被稀释。
    """

    def __init__(self):
        super().__init__("AI 天花板公平性测试（v6.9.47-10）")

    def setup(self):
        self.tmp_root = create_isolated_env()
        self._opt = _load_optimize_module(self.tmp_root)

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    @staticmethod
    def _mk_sections(texts: dict):
        """构造 read_section stub（零文件 IO）。"""
        class _StubSections:
            def read_section(self, key):
                return texts.get(key, "")
        return _StubSections()

    # 干净填充文本（不含任何敏感词，纯凑字数）
    _FILLER = "甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥" * 600  # ~13.2K 字

    def run_tests(self):
        opt = self._opt
        filler = self._FILLER

        # 10.1 白名单：'关键科学问题'不计入'关键'计数
        res = opt._detect_ai_patterns(
            Path(self.tmp_root),
            self._mk_sections({"rationale": "关键科学问题K1。关键科学问题K2。关键科学问题K3。",
                               "content": "", "scheme": ""}),
        )
        found = res["details"]["redundant_modifiers"]["found"]
        self.assert_true(found.get("关键", 0) == 0,
                         "白名单术语'关键科学问题'不应计入'关键'")

        # 10.2 白名单：'系统误差/有效性/同时电离'同理剔除
        res2 = opt._detect_ai_patterns(
            Path(self.tmp_root),
            self._mk_sections({"rationale": "系统误差是主要误差来源。修正项有效性判据。同时电离通道。",
                               "content": "", "scheme": ""}),
        )
        found2 = res2["details"]["redundant_modifiers"]["found"]
        found2t = res2["details"]["transition_words"]["found"]
        self.assert_true(found2.get("系统", 0) == 0, "'系统误差'不应计入'系统'")
        self.assert_true(found2.get("有效", 0) == 0, "'有效性'不应计入'有效'")
        self.assert_true(found2t.get("同时", 0) == 0, "'同时电离'不应计入'同时'")

        # 10.2b 白名单长词优先（v6.9.50）：'同时或近同时电离'必须先于
        # '同时电离'遮蔽，否则长词尾部被短词占位后残余"同时或近"中的
        # "同时"泄漏计数 1 次（08-24 健康检查实证）
        res2b = opt._detect_ai_patterns(
            Path(self.tmp_root),
            self._mk_sections({"rationale": "一个以上电子被同时或近同时电离的过程。",
                               "content": "", "scheme": ""}),
        )
        found2bt = res2b["details"]["transition_words"]["found"]
        self.assert_true(found2bt.get("同时", 0) == 0,
                         "'同时或近同时电离'不应因遮蔽顺序泄漏'同时'计数")

        # 10.3 阈值千字归一：13K 字长文冗余 16 次（~1.2/千字，正常密度）不扣分
        # filler 13.2K 字 → 阈值 max(12, 26)；16 次真实冗余用法 < 26 → 不扣
        text_long = filler + ("该方案显著且良好。" * 6 + "重要完整成熟精准。" * 1)  # 显×6 良×6 + 重完成精×4 = 16 次
        res3 = opt._detect_ai_patterns(
            Path(self.tmp_root),
            self._mk_sections({"rationale": text_long, "content": "", "scheme": ""}),
        )
        self.assert_true(
            res3["details"]["redundant_modifiers"]["count"] == 16,
            "长文冗余词计数应为 16（filler 不含敏感词）",
        )
        self.assert_true(
            res3["details"]["redundant_modifiers"]["penalty"] == 0,
            "13K 字文本冗余 16 次（~1.2/千字正常密度）不应扣分（v6.9.47 千字归一）",
        )

        # 10.4 短文本仍严格：2K 字 20 次（10/千字）照扣
        short_text = ("甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥" * 90
                      + "显著重要良好成熟完整精准。" * 3)  # ~2K 字 + 18 次
        res4 = opt._detect_ai_patterns(
            Path(self.tmp_root),
            self._mk_sections({"rationale": short_text, "content": "", "scheme": ""}),
        )
        self.assert_true(
            res4["details"]["redundant_modifiers"]["penalty"] > 0,
            "2K 字文本冗余 18 次（~9/千字）仍应扣分（防归一化把检测废掉）",
        )

        # 10.5 raw_ceiling：floor 掩埋修复——raw 可低于 0.5，ceiling 报 0.5
        heavy = filler + "在此基础上，在此基础上，在此基础上，在此基础上。" * 20
        res5 = opt._detect_ai_patterns(
            Path(self.tmp_root),
            self._mk_sections({"rationale": heavy, "content": "", "scheme": ""}),
        )
        self.assert_true(res5["ceiling"] == 0.5, "重扣分时 ceiling 应为 floor 0.5")
        self.assert_true(res5["raw_ceiling"] < 0.5,
                         "raw_ceiling 应保留 floor 前原始值（复检可见真实进步）")
        self.assert_true("raw_ceiling" in res5, "返回结构应含 raw_ceiling 字段")

        # 10.6 章节级检测：scheme 干净时 section_key="scheme" 口径无扣分
        bad_rationale = "显著重要良好成熟完整精准。" * 10  # 60 次冗余
        res6 = opt._detect_ai_patterns(
            Path(self.tmp_root),
            self._mk_sections({"rationale": bad_rationale, "content": "", "scheme": filler}),
            section_key="scheme",
        )
        self.assert_true(
            res6["details"]["redundant_modifiers"]["penalty"] == 0,
            "章节级检测只看聚焦章节（scheme 干净 → 无扣分）",
        )
        self.assert_true(res6.get("section_key") == "scheme", "应回传 section_key")

        # 10.7 长句免赔额：13K 文本 5 处长句，免赔 2+1=3 处，只扣 2 处
        long_sentence = "这" * 130 + "。"
        text_ls = filler + long_sentence * 5
        res7 = opt._detect_ai_patterns(
            Path(self.tmp_root),
            self._mk_sections({"rationale": text_ls, "content": "", "scheme": ""}),
        )
        ls = res7["details"]["long_sentences"]
        self.assert_true(ls["severe_count"] == 5, "应检出 5 处长句")
        expected_penalty = (5 - ls["free_quota"]) * 0.02
        self.assert_true(
            abs(ls["penalty"] - expected_penalty) < 1e-6 and expected_penalty < 5 * 0.02,
            f"长句应享免赔额（free={ls['free_quota']}，扣 {expected_penalty} 而非 0.10）",
        )

        # 10.8 源码守卫：executor 复检必须用 raw 比较 + 章节级归因
        exec_src = (Path(__file__).parent.parent / "lifecycle" / "executor.py").read_text(encoding="utf-8")
        self.assert_true(
            'ai_check.get("raw_ceiling"' in exec_src,
            "executor 复检应取 raw_ceiling（floor 前值）",
        )
        self.assert_true(
            "section_baseline" in exec_src,
            "executor 应建立章节级复检基线",
        )
        self.assert_true(
            "章节原始天花板" in exec_src,
            "复检日志应区分章节口径与全局口径",
        )
        # optimize.py 返回结构守卫
        opt_src = (Path(__file__).parent.parent / "proposal_lifecycle" / "optimize.py").read_text(encoding="utf-8")
        self.assert_true(
            'AI_TERM_WHITELIST' in opt_src and '关键科学问题' in opt_src,
            "optimize.py 应存在领域术语白名单",
        )
        self.assert_true(
            "text_for_count" in opt_src,
            "计数应基于白名单过滤后的文本",
        )
        # writer prompt 量化清单守卫
        self.assert_true(
            "逐词清单" in opt_src,
            "writer prompt 应含逐词量化修复清单",
        )


class SectionHygieneTests(TestSuite):
    """11：v6.9.53 章节卫生——字数预算预检 + full_review 骨架化 + references 清洗。"""

    def __init__(self):
        super().__init__("章节卫生与字数预算测试（v6.9.53-11）")

    def setup(self):
        import tempfile
        self.tmp = Path(tempfile.mkdtemp())
        # 隔离加载 section_hygiene
        for mod in list(sys.modules):
            if mod == "proposal_lifecycle.section_hygiene":
                del sys.modules[mod]
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from proposal_lifecycle import section_hygiene
        self.sh = section_hygiene

    def teardown(self):
        if self.tmp and self.tmp.exists():
            shutil.rmtree(self.tmp, ignore_errors=True)

    def run_tests(self):
        sh = self.sh
        sec = self.tmp / "04_proposal" / "sections"
        sec.mkdir(parents=True)

        # 11.1 体量参考报告：分级判定 + 偏短提示（v6.9.55 起纯信息性）
        (sec / "rationale.md").write_text("正" * 11000, encoding="utf-8")
        (sec / "content.md").write_text("正" * 5500, encoding="utf-8")
        rep = sh.budget_report(sec)
        self.assert_true(rep["rationale"]["status"] == "over", "rationale 11000 字应标 over")
        self.assert_true(rep["content"]["status"] == "ok", "content 5500 字应标 ok")
        txt = sh.budget_report_text(sec, focus_key="rationale")
        self.assert_true("非门限" in txt, "体量表应明示非门限（质量才是判据）")
        self.assert_true("净删" not in txt, "v6.9.55 起不应输出净删式字数指令")

        # 11.2 full_review 迁移 + 骨架重写 + 幂等
        (sec / "scheme.md").write_text(
            "# 研究方案\n\n## 总体方案\n正文。\n\n## 技术路线\n正文。\n", encoding="utf-8")
        (sec / "full_review.md").write_text(
            "# 核查记录\n\n经前 5 轮评审修复确认，本轮 round-6 重新核查未见复发。\n" * 40,
            encoding="utf-8")
        out = sh.migrate_full_review_record(self.tmp, dry_run=False)
        self.assert_true(out and Path(out).exists(), "核查记录应迁至 05_review/")
        fr = (sec / "full_review.md").read_text(encoding="utf-8")
        self.assert_true("round-6" not in fr, "骨架不应含轮次工作记录")
        self.assert_true("技术路线" in fr, "骨架应含章节标题索引")
        self.assert_true(sh.migrate_full_review_record(self.tmp) is None,
                         "干净骨架二次执行应幂等跳过")

        # 11.3 references 工作日志剥离：保留条目、剥离表格
        entries = "\n".join(
            f"[{i}] Zhang Y. et al. *Paper {i}*. **Nature {i}, 100 (2020).**"
            for i in range(1, 36))
        (sec / "references.md").write_text(
            "# 参考文献\n\n" + entries +
            "\n\n## §D 引用挂钩映射表\n\n| [CITE:a] | 3 | 8 | x |\n| [CITE:b] | 4 | 9 | y |\n"
            "| [CITE:c] | 5 | 10 | z |\n\n## §E 核实声明\n已逐条核实。\n",
            encoding="utf-8")
        out2 = sh.strip_references_worklog(self.tmp, dry_run=False)
        self.assert_true(out2 and Path(out2).exists(), "工作日志段落应剥离迁出")
        ref = (sec / "references.md").read_text(encoding="utf-8")
        self.assert_true("| [CITE:" not in ref and "核实声明" not in ref,
                         "剥离后不应残留工作日志")
        self.assert_true("[35]" in ref and "[1]" in ref, "全部文献条目必须保留")

        # 11.4 源码守卫：critic 排除 full_review + 附预检；writer 骨架指令
        opt_src = (Path(__file__).parent.parent / "proposal_lifecycle" / "optimize.py").read_text(encoding="utf-8")
        self.assert_true(
            'and s[\'key\'] not in ("references", "full_review")' in opt_src,
            "full_review critic 文件列表应同时排除 references 与 full_review",
        )
        self.assert_true(
            "budget_report_text(" in opt_src and "full_review_purity_text(" in opt_src,
            "critic 应附字数预算与纯净性预检",
        )
        self.assert_true(
            "focus_key=focus_section[\"key\"]" in opt_src,
            "章节级 critic 应附聚焦章节预算",
        )
        self.assert_true(
            "全文逻辑骨架" in opt_src and "≤3000 字" in opt_src,
            "writer 应含 full_review 骨架写法指令",
        )
        self.assert_true(
            "内容质量纪律" in opt_src and "writer_quality_text" in opt_src,
            "writer 应含质量纪律与缺陷指令注入（v6.9.55 质量口径）",
        )
        self.assert_true(
            "full_review.md 同样适用" in opt_src,
            "纯净性红线应扩展覆盖 full_review.md",
        )

        # 11.5 standards 守卫：预算条目已写入
        std = json.loads((Path(__file__).parent.parent.parent / "memory" / "nsfc-standards.json").read_text(encoding="utf-8"))
        ss = std["general_principles"]["section_standards"]
        self.assert_true(
            any("参考体量4000-7000" in x for x in ss["content"]),
            "content 标准应含 4000-7000 参考体量（非门限）",
        )
        self.assert_true(
            any("参考体量6000-10000" in x for x in ss["scheme"]),
            "scheme 标准应含 6000-10000 参考体量（非门限）",
        )
        self.assert_true(
            any("字数非门限" in x for x in ss["content"] + ss["scheme"] + ss["rationale"]),
            "standards 应明示质量核心口径（字数非门限）",
        )
        self.assert_true(
            any("3000" in x for x in ss["full_review"]),
            "full_review 标准应含骨架字数上限",
        )

        # ================================================================
        # 12（v6.9.54 引入，v6.9.55 质量核心重构）: 写入门卫 + 质量门
        # 拦截判据：冗余（跨章节/章节内重复）与无关内容——字数仅上下文
        # ================================================================
        # 12.1 质量门核心语义：超限但无缺陷 = 实质性长文 → 放行
        sec2 = self.tmp / "g1" / "04_proposal" / "sections"
        sec2.mkdir(parents=True)
        long_unique = "、".join(f"不同论证句编号{i}涉及HHG谱学机制差异分析" for i in range(500))
        (sec2 / "content.md").write_text(long_unique, encoding="utf-8")
        r = sh.quality_gate(sec2, "content", before_chars=0, prop_dir=self.tmp / "g1")
        self.assert_true(
            r["passed"] and r["over_budget"],
            "超参考体量但冗余/无关零命中应放行（实质性长文）",
        )
        self.assert_true("实质性长文" in r["reason"], "放行理由应说明密度合格")

        # 12.2 跨章节重复句（归一化相同）→ 拦截
        dup_sentence = "该体系的Floquet能带工程调控HHG产额的机制已被多组实验证实并形成共识"
        (sec2 / "rationale.md").write_text(
            "立项依据首段。" + dup_sentence + "。补充论述一。", encoding="utf-8")
        (sec2 / "scheme.md").write_text(
            "方案首段。" + dup_sentence + "。补充论述二。", encoding="utf-8")
        r = sh.quality_gate(sec2, "scheme", before_chars=100, prop_dir=self.tmp / "g1")
        self.assert_true(not r["passed"], "跨章节重复句应拦截（NSFC 评审红线）")
        self.assert_true("跨章节重复句" in r["reason"], "拦截理由应指向跨章节重复")

        # 12.3 章节内成片重复（≥3 次相同句）→ 拦截
        sec3 = self.tmp / "g2" / "04_proposal" / "sections"
        sec3.mkdir(parents=True)
        rep_sent = "通过双色场相位控制可以实现量子几何张量分量的选择性激发与读出验证"
        (sec3 / "rationale.md").write_text(
            ("开场。" + rep_sent + "。") * 4, encoding="utf-8")
        (sec3 / "content.md").write_text("内容章独立。", encoding="utf-8")
        (sec3 / "scheme.md").write_text("方案章独立。", encoding="utf-8")
        r = sh.quality_gate(sec3, "rationale", before_chars=100, prop_dir=self.tmp / "g2")
        self.assert_true(not r["passed"], "章节内重复论证 ≥3 组应拦截")
        self.assert_true("章节内重复" in r["reason"], "拦截理由应指向章节内重复")

        # 12.4 无关内容：程序不拦截（语义判断交 LLM），但产生复核线索
        sec4 = self.tmp / "general-hhg-floquet-test-20260101" / "04_proposal" / "sections"
        sec4.mkdir(parents=True)
        # 核心术语 hhg/floquet；无关段（零术语、句句不同——纯无关场景，
        # 不混入章节内重复以免同时触发程序化拦截）
        off_paras = [
            f"本课题的研究将推动相关领域的发展方向{i}，具有重要的理论意义与突出的"
            f"实际应用价值{i}，可以为后续一系列研究工作提供坚实的理论基础和有益的"
            f"方法学参考，也能够为同领域其他课题组开展类似探索提供可借鉴的技术路线"
            f"与数据分析范式，从而在更广泛的层面上促进该方向的持续发展与深化，"
            f"并为跨学科的方法迁移与理论融合创造切实可行的条件与新的可能性。"
            for i in range(1, 7)
        ]
        (sec4 / "content.md").write_text("\n\n".join(off_paras), encoding="utf-8")
        (sec4 / "rationale.md").write_text("HHG 与 Floquet 调控的立项论述。" * 3, encoding="utf-8")
        (sec4 / "scheme.md").write_text("HHG Floquet 实验方案论述。" * 3, encoding="utf-8")
        r = sh.quality_gate(sec4, "content", before_chars=0,
                            prop_dir=self.tmp / "general-hhg-floquet-test-20260101")
        self.assert_true(
            r["passed"],
            "无关内容不程序拦截（语义判断交 LLM，防中文论证段误伤）",
        )
        self.assert_true(
            len(r.get("irrelevant") or []) > 0,
            "疑似无关段应作为线索携带（供 prompt 注入 LLM 复核）",
        )
        dirs_txt = sh.quality_directives_text(
            self.tmp / "general-hhg-floquet-test-20260101", focus_key="content")
        self.assert_true(
            "相关性复核线索" in dirs_txt and "语义裁决" in dirs_txt,
            "质量指令应含无关段复核线索（LLM 裁决口径）",
        )

        # 12.5 干净章节 → 通过；references 恒通过
        r = sh.quality_gate(sec4, "scheme", before_chars=None,
                            prop_dir=self.tmp / "general-hhg-floquet-test-20260101")
        self.assert_true(r["passed"], "干净章节应通过质量门")
        r = sh.quality_gate(sec4, "references", before_chars=100, prop_dir=None)
        self.assert_true(r["passed"], "references 无体量参考应恒通过")

        # 12.5b（v6.9.59 回归）：正文存在跨章节重复时，references/
        # full_review 的 writer 物理上无法修复正文冗余（指令约束只改
        # 聚焦章节文件），不得被全局 cross 判据误拦导致晋级主路径封死
        # （v6.9.55 重构丢失 v6.9.54 "无预算章节"出口的回归）。
        dup_sentence = (
            "本课题围绕强场物理与超快光学的交叉前沿展开系统性研究并建立定量表征框架。"
        )
        (sec4 / "rationale.md").write_text(
            dup_sentence + "\n\n立项背景论述补充。" * 5, encoding="utf-8")
        (sec4 / "content.md").write_text(
            dup_sentence + "\n\n研究内容分层论述补充。" * 5, encoding="utf-8")
        r_body = sh.quality_gate(sec4, "rationale", before_chars=100,
                                 prop_dir=self.tmp / "general-hhg-floquet-test-20260101")
        self.assert_true(
            not r_body["passed"], "正文章节跨章节重复仍应拦截（评审红线）")
        for non_body in ("references", "full_review"):
            r_nb = sh.quality_gate(sec4, non_body, before_chars=100,
                                   prop_dir=self.tmp / "general-hhg-floquet-test-20260101")
            self.assert_true(
                r_nb["passed"],
                f"{non_body} 不应被正文跨章节冗余误拦（writer 无权改正文）",
            )
        # 12.5c（v6.9.59 设计边界固化）：detect_redundancy 只扫描三个
        # 正文章节（L480），references/full_review 的结构卫生由写入门卫
        # （guard_written_artifacts：工作日志剥离/骨架迁移）专职负责，
        # 质量门对二者为"零信息通过"——句子重复检测对文献条目列表天然
        # 失真（条目格式相似会误报），此分工即 v6.9.54"无预算章节恒
        # 通过"出口的本意。此处固化该边界，防止未来误扩展。
        (sec4 / "references.md").write_text(
            "# 参考文献\n\n" + (dup_sentence + "\n\n") * 3, encoding="utf-8")
        r_within = sh.quality_gate(sec4, "references", before_chars=100,
                                   prop_dir=self.tmp / "general-hhg-floquet-test-20260101")
        self.assert_true(
            r_within["passed"],
            "references 不在 detect_redundancy 扫描范围，质量门零信息通过（卫生归 guard）")
        g_ref = sh.strip_references_worklog(self.tmp / "general-hhg-floquet-test-20260101")
        self.assert_true(
            g_ref is None or isinstance(g_ref, str),
            "references 结构卫生走专职 guard 路径（不抛异常即通过）")
        (sec4 / "references.md").write_text(
            "# 参考文献\n\n[1] Zhang Y. et al. Nature 1, 1 (2020).\n",
            encoding="utf-8")

        # 12.6 写入门卫：污染落盘后当场修复（零存活）
        (sec3 / "scheme.md").write_text(
            "# 研究方案\n\n## 总体方案\n正文。\n", encoding="utf-8")
        (sec3 / "full_review.md").write_text(
            "核查记录 round-9 修复确认表\n" * 30, encoding="utf-8")
        entries = "\n".join(
            f"[{i}] Zhang Y. et al. *P{i}*. **Nature {i}, 1 (2020).**"
            for i in range(1, 31))
        (sec3 / "references.md").write_text(
            "# 参考文献\n\n" + entries +
            "\n\n## §D 映射表\n\n| [CITE:a] | 1 | 2 | x |\n| [CITE:b] | 2 | 3 | y |\n"
            "| [CITE:c] | 3 | 4 | z |\n", encoding="utf-8")
        g = sh.guard_written_artifacts(self.tmp / "g2")
        self.assert_true(
            any("full_review" in x for x in g["repaired"]),
            "门卫应修复 full_review 污染",
        )
        self.assert_true(
            any("references" in x for x in g["repaired"]),
            "门卫应剥离 references 工作日志",
        )
        fr3 = (sec3 / "full_review.md").read_text(encoding="utf-8")
        ref3 = (sec3 / "references.md").read_text(encoding="utf-8")
        self.assert_true("round-9" not in fr3, "门卫后骨架应无污染")
        self.assert_true("[CITE:" not in ref3 and "[30]" in ref3,
                         "门卫后文献应无损且无工作日志")

        # 12.7 源码守卫：executor 接入门卫与质量门（v6.9.55 质量口径）
        exec_src = (Path(__file__).parent.parent / "lifecycle" / "executor.py").read_text(encoding="utf-8")
        self.assert_true(
            "guard_written_artifacts(prop_dir)" in exec_src,
            "writer 成功后应执行写入门卫",
        )
        self.assert_true(
            "quality_gate(" in exec_src,
            "writer 后应执行质量门判定",
        )
        self.assert_true(
            "and quality_ok" in exec_src,
            "section_passed 应纳入质量门",
        )
        self.assert_true(
            "quality_gate_passed" in exec_src,
            "质量门判定应入 score_history 可观测",
        )
        self.assert_true(
            "budget_gate(" not in exec_src,
            "v6.9.55 起字数门应被质量门取代（不得残留）",
        )

        # 12.8 optimize 源码守卫：质量指令为主、字数为辅
        opt_src = (Path(__file__).parent.parent / "proposal_lifecycle" / "optimize.py").read_text(encoding="utf-8")
        self.assert_true(
            "quality_directives_text" in opt_src,
            "writer/critic 应注入质量缺陷指令（具体冗余位置）",
        )
        self.assert_true(
            "内容质量纪律" in opt_src and "不以字数论" in opt_src,
            "writer 纪律段应以质量为核心表述",
        )
        self.assert_true(
            "非门限" in sh.budget_report_text(sec4, focus_key="content")
            or "非门限" in (sh.budget_report_text(sec4) or ""),
            "体量表应明示非门限语义",
        )

        # ================================================================
        # 13（v6.9.60）: 同构问题治理——手册单一真相源 / critic digest / 晋级完整性门
        # ================================================================
        # 13.1 critic 报告 digest：小报告不触发，大报告生成且限额
        d1 = self.tmp / "d1" / "05_review"
        d1.mkdir(parents=True)
        small = d1 / "critic-round-1.md"
        small.write_text("# 报告\n- [high] 问题一。\n", encoding="utf-8")
        self.assert_true(
            sh.build_critic_digest(small) is None,
            "小报告（≤25KB）不应生成 digest",
        )
        big = d1 / "critic-round-2.md"
        body = "\n".join(
            f"叙述段落第{i}行，包含大量背景铺垫与语境说明文字内容用于膨胀。"
            for i in range(700))
        big.write_text(
            "# 检验报告\n## 问题清单\n- [critical] 核心问题：指标口径矛盾。\n"
            "- [high] 次要问题：术语不统一。\n" + body + "\n## 评分\n综合评分：0.72\n",
            encoding="utf-8")
        dg = sh.build_critic_digest(big)
        self.assert_true(dg is not None and dg.exists(), "大报告应生成 digest")
        dtext = dg.read_text(encoding="utf-8")
        self.assert_true(
            len(dtext.encode("utf-8")) <= sh.CRITIC_DIGEST_MAX_BYTES + 200,
            "digest 应守住字节上限",
        )
        self.assert_true(
            "[critical]" in dtext and "综合评分" in dtext,
            "digest 应保留 severity 行与评分块",
        )
        self.assert_true(
            "叙述段落第300行" not in dtext,
            "digest 应丢弃纯叙述行",
        )

        # 13.2 手册迁移：归档 + stub + 幂等 + canonical 缺失时落位
        m1 = self.tmp / "m1"
        (m1 / "04_proposal").mkdir(parents=True)
        (m1 / "04_proposal" / "methodology-manual.md").write_text(
            "# 旧手册\nwriter 写的细节内容。\n" * 100, encoding="utf-8")
        out = sh.migrate_methodology_manual(m1, dry_run=False)
        self.assert_true(out and Path(out).exists(), "旧手册应归档至 05_review")
        canon = m1 / "03_method" / "method-manual.md"
        self.assert_true(
            canon.exists() and canon.stat().st_size > 100,
            "canonical 缺失时应从旧文件落位（防指针悬空）",
        )
        stub = (m1 / "04_proposal" / "methodology-manual.md").read_text(encoding="utf-8")
        self.assert_true(
            "03_method/method-manual.md" in stub and "唯一真相源" in stub,
            "原位应留 stub 指针",
        )
        self.assert_true(
            sh.migrate_methodology_manual(m1) is None,
            "stub 状态二次迁移应幂等跳过",
        )

        # 13.3 optimize 源码守卫：digest 接入 + 手册路径 + writer 不写手册
        self.assert_true(
            "build_critic_digest" in opt_src,
            "writer 应接入 critic 报告 digest（大报告瘦身）",
        )
        self.assert_true(
            opt_src.count('"03_method" / "method-manual.md"') >= 2,
            "手册路径应统一为 03_method 单一真相源",
        )
        self.assert_true(
            "不由本步骤更新" in opt_src,
            "writer prompt 应声明手册由专职步骤维护（消除双写）",
        )
        exec_src2 = (Path(__file__).parent.parent / "lifecycle" / "executor.py").read_text(encoding="utf-8")
        self.assert_true(
            "手册质量纪律" in exec_src2,
            "update_method_manual 步骤应含手册质量纪律（去重/禁追加）",
        )

        # 13.4 晋级完整性门源码守卫
        ms_src = (Path(__file__).parent.parent / "lifecycle" / "micro_scheduler.py").read_text(encoding="utf-8")
        self.assert_true(
            "暂缓晋级" in ms_src and "晋级完整性门" in ms_src,
            "_check_and_transition 应含晋级完整性门（非 done job 暂缓）",
        )


def main():
    from test_runner import print_report

    suites = []
    for cls in (AnchorOrderTests, WriterEscalationTests, SemanticDedupTests, ExecutorPathTests,
                WeeklyResetAnchorTests, TaskSyncRollbackTests, KbDistillAutoTests, NamingGuardTests,
                ReferencesPreflightTests, MetricsPreflightTests, AICeilingFairnessTests,
                SectionHygieneTests):
        s = cls()
        s.setup()
        s.run_tests()
        s.teardown()
        suites.append(s)
    print_report(suites)


if __name__ == "__main__":
    main()
