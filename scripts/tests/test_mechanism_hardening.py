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


def main():
    from test_runner import print_report

    suites = []
    for cls in (AnchorOrderTests, WriterEscalationTests, SemanticDedupTests, ExecutorPathTests,
                WeeklyResetAnchorTests, TaskSyncRollbackTests, KbDistillAutoTests, NamingGuardTests):
        s = cls()
        s.setup()
        s.run_tests()
        s.teardown()
        suites.append(s)
    print_report(suites)


if __name__ == "__main__":
    main()
