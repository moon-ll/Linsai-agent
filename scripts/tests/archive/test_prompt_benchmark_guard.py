#!/usr/bin/env python3
"""
test_prompt_benchmark_guard.py — prompt 自优化架构加固回归测试（v6.9.9）

覆盖三项改进：
    1. 范本守门（_benchmark_conflict_guard）：与范本实测口径冲突的量化
       指令（总字数下限、章节字数下限、文献篇数区间、评分魔法数）被拦截，
       合法口径通过；_apply_suggestions 集成路径守门生效（文件不写入）
    2. 指令化模板：score_analysis 建议的 content 为可执行指令（非
       "需在 prompt 中要求…"元描述），且被回收标记注释包裹
    3. 自动段回收（_reap_stale_auto_sections）：过期+问题未复现 → 删除；
       过期+问题复现 → 保留；未过期 → 保留；pat="-" 来源 → 保留；
       回收后正文其余部分不受影响、回收前自动备份

历史污染实例（守门必须能拦截的回归锚点）：
    - "总字数 ≥ 4000 字"（范本仅立项依据即 5000-8000 字）
    - "15-30 篇区间"（范本实测 30-40 篇）
    - "占位符给 0.10 而非 0.00"（与运行时四维评分双口径）

注意：本测试不调用 LLM、不触碰真实 ~/.hermes，全部运行于隔离临时目录。
"""

import shutil
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, REAL_ROOT


def _utc_stamped(days_ago: int = 0) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


class PromptBenchmarkGuardTests(TestSuite):
    def __init__(self):
        super().__init__("prompt 范本守门与自动段回收测试（v6.9.9）")
        self.tmp_root = None
        self.po = None
        self._orig = {}

    # ------------------------------------------------------------------
    # 隔离环境：临时 profiles 目录 + 临时 suggestions/backups
    # ------------------------------------------------------------------

    def setup(self):
        self.tmp_root = create_isolated_env()

        fake_home = self.tmp_root / "fakehome"
        profiles = fake_home / ".hermes" / "profiles"
        for prof in ("writer", "critic"):
            (profiles / prof).mkdir(parents=True, exist_ok=True)
            (profiles / prof / "SOUL.md").write_text(
                f"# {prof.title()} Profile\n\n正文基线内容。\n", encoding="utf-8"
            )
        (self.tmp_root / "memory").mkdir(parents=True, exist_ok=True)

        if "prompt_optimizer" in sys.modules:
            del sys.modules["prompt_optimizer"]
        sys.path.insert(0, str(REAL_ROOT / "scripts"))
        import prompt_optimizer as po
        self.po = po

        self._orig = {
            "HERMES_PROFILES_DIR": po.HERMES_PROFILES_DIR,
            "SUGGESTIONS_PATH": po.SUGGESTIONS_PATH,
            "BACKUPS_DIR": po.BACKUPS_DIR,
        }
        po.HERMES_PROFILES_DIR = profiles
        po.SUGGESTIONS_PATH = self.tmp_root / "memory" / "prompt-suggestions.json"
        po.BACKUPS_DIR = self.tmp_root / "memory" / "prompt-backups"

    def teardown(self):
        if self.po:
            for k, v in self._orig.items():
                setattr(self.po, k, v)
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)
        if str(REAL_ROOT / "scripts") in sys.path:
            sys.path.remove(str(REAL_ROOT / "scripts"))

    def run_tests(self):
        self._test_guard_blocks_known_pollution()
        self._test_guard_passes_legitimate()
        self._test_apply_suggestions_guard_integration()
        self._test_score_analysis_content_is_instructional()
        self._test_wrap_auto_section_roundtrip()
        self._test_reap_removes_stale_unrecurring()
        self._test_reap_keeps_recurring()
        self._test_reap_keeps_fresh_and_foreign()
        self._test_reap_mixed()
        self._test_reap_creates_backup()

    def _mk_suggestion(self, content: str, target: str = "writer", **kw):
        s = {
            "id": kw.pop("sid", "ps-test-0001"),
            "source": "agent_score_analysis",
            "target_profile": target,
            "target_file": str(self.po.HERMES_PROFILES_DIR / target / "SOUL.md"),
            "target_file_display": f"~/.hermes/profiles/{target}/SOUL.md",
            "priority": "high",
            "action": "append",
            "content": content,
            "description": "测试建议",
            "fingerprint": "fp-test",
            "status": "pending",
            "created_at": _utc_stamped(),
        }
        s.update(kw)
        return s

    # ------------------------------------------------------------------
    # 1. 范本守门
    # ------------------------------------------------------------------

    def _test_guard_blocks_known_pollution(self):
        """三类历史污染 + 压线区间必须被拦截。"""
        blocked = [
            "请基于 brief 实质扩写申请书，总字数 ≥ 4000 字，每章节 ≥ 1200 字",
            "参考文献总数是否在 15-30 篇区间",
            "当申请书内容为占位符时，给 0.10 而非 0.00",
            "参考文献控制在 20-30 篇",
        ]
        for content in blocked:
            r = self.po._benchmark_conflict_guard({"content": content})
            self.assert_true(r is not None, f"应拦截：{content}")

    def _test_guard_passes_legitimate(self):
        """合法口径与无量化指令必须通过。"""
        passed = [
            "立项依据 5000-8000 字，参考文献 30-40 篇",
            "参考文献总数在 20-40 篇区间（范本 30-40 为标杆）",
            "每章节 ≥ 3000 字",
            "全文 25000 字以上",
            "逐条核对评审报告的每个问题并逐一修改",
        ]
        for content in passed:
            r = self.po._benchmark_conflict_guard({"content": content})
            self.assert_true(r is None, f"应通过：{content}（误拦：{r}）")

    def _test_apply_suggestions_guard_integration(self):
        """_apply_suggestions 集成：守门命中的建议 status=rejected_guard 且文件未写入。"""
        soul = self.po.HERMES_PROFILES_DIR / "writer" / "SOUL.md"
        before = soul.read_text(encoding="utf-8")

        bad = self._mk_suggestion(
            "\n## 自动优化规则\n\n总字数 ≥ 4000 字，每章节 ≥ 1200 字\n",
            sid="ps-bad-0001",
        )
        good = self._mk_suggestion(
            self.po._wrap_auto_section(
                "## 自动优化规则（评分分析 2 次证据）\n\n逐条核对评审报告的每个问题并逐一修改。\n",
                sid="ps-good-0001", pat="-",
            ),
            sid="ps-good-0001",
        )
        self.po._apply_suggestions([bad, good], [bad, good], auto_mode=True, backup_count_tracker={})

        self.assert_eq(bad.get("status"), "rejected_guard", "污染建议应被守门拒绝")
        self.assert_true("guard_reason" in bad, "拒绝原因应记录")
        self.assert_eq(good.get("status"), "applied", "合法建议应正常应用")

        after = soul.read_text(encoding="utf-8")
        self.assert_true("总字数 ≥ 4000 字" not in after, "污染内容不得写入 SOUL.md")
        self.assert_true("逐条核对评审报告的每个问题" in after, "合法内容应写入 SOUL.md")
        self.assert_true(after.startswith(before.rstrip()[:20]), "SOUL.md 原有内容保持不变")

    # ------------------------------------------------------------------
    # 2. 指令化模板
    # ------------------------------------------------------------------

    def _test_score_analysis_content_is_instructional(self):
        """score_analysis 生成的 content 必须是可执行指令且带回收标记。"""
        reasons = [
            {"agent": "writer", "reason": "writer 提交与上一轮相同的文件，MD5 完全一致，无实质性修改", "round_ref": "r3"},
        ]
        hints = self.po._analyze_reasons_for_prompt_hints(reasons)
        self.assert_true(len(hints) >= 1, "应识别出零修改模式")
        hint = hints[0]
        self.assert_true("instruction" in hint, "hint 应带 instruction 字段")
        self.assert_true(
            "需在 prompt 中" not in hint["instruction"] and "需强化" not in hint["instruction"],
            f"指令不得是元描述：{hint['instruction'][:40]}",
        )

        # 走完整生成路径验证 content 带标记
        suggestions = self.po._generate_suggestions(
            [], reasons, [], self.po._discover_prompt_files()
        )
        score_sug = [s for s in suggestions if s.get("source") == "agent_score_analysis"]
        self.assert_true(len(score_sug) >= 1, "应生成 score_analysis 建议")
        content = score_sug[0]["content"]
        self.assert_true("<!--auto-opt:start:" in content, "content 应被回收标记包裹")
        m = self.po.AUTO_TAG_RE.search(content)
        self.assert_true(m is not None, "标记应可被回收正则解析")
        self.assert_true(
            m.group(3) and m.group(3) != "-",
            f"score_analysis 段应内嵌 pattern_re：{m.group(3)[:30]}",
        )

    def _test_wrap_auto_section_roundtrip(self):
        """标记包裹与解析往返一致；多段共存互不干扰。"""
        sid1, sid2 = "ps-aaa-1111", "ps-bbb-2222"
        s1 = self.po._wrap_auto_section("## 自动优化规则\n\n规则一内容。\n", sid=sid1, pat=r"零修改|无实质性")
        s2 = self.po._wrap_auto_section("## 自动优化规则\n\n规则二内容。\n", sid=sid2, pat="-")
        both = s1 + "\n中间正文\n" + s2
        ms = list(self.po.AUTO_TAG_RE.finditer(both))
        self.assert_eq(len(ms), 2, "多段共存应解析出 2 段")
        self.assert_eq(ms[0].group(1), sid1, "第一段 sid 正确")
        self.assert_eq(ms[0].group(3), r"零修改|无实质性", "第一段 pattern_re 正确")
        self.assert_eq(ms[1].group(3), "-", "第二段 pat='-'")

    # ------------------------------------------------------------------
    # 3. 自动段回收
    # ------------------------------------------------------------------

    def _write_soul_with_sections(self, target: str, sections):
        """sections: list of (sid, days_ago, pat, body)"""
        soul = self.po.HERMES_PROFILES_DIR / target / "SOUL.md"
        parts = ["# 基线正文开始\n\n正文第一段。\n"]
        for sid, days_ago, pat, body in sections:
            # 直接构造带历史时间戳的标记（绕过 _wrap_auto_section 的当前时间）
            ts = _utc_stamped(days_ago=days_ago)
            start = f"<!--auto-opt:start:{sid}:{ts}:{pat}-->"
            end = f"<!--auto-opt:end:{sid}-->"
            parts.append(f"\n{start}\n{body}\n{end}\n")
        parts.append("\n结尾正文。\n")
        soul.write_text("".join(parts), encoding="utf-8")
        return soul

    def _test_reap_removes_stale_unrecurring(self):
        """过期(20天)+问题未复现 → 删除；正文其余部分不变。"""
        soul = self._write_soul_with_sections("writer", [
            ("ps-old-0001", 20, r"零修改|无实质性", "## 自动优化规则\n\n逐条核对每个问题。\n"),
        ])
        # 近期 reasons 不含该模式
        reasons = [{"agent": "writer", "reason": "其他无关问题", "round_ref": ""}]
        reaped = self.po._reap_stale_auto_sections(reasons)
        self.assert_eq(reaped, 1, "应回收 1 段")
        after = soul.read_text(encoding="utf-8")
        self.assert_true("ps-old-0001" not in after, "过期段应被删除")
        self.assert_true("正文第一段。" in after and "结尾正文。" in after, "正文不受影响")

    def _test_reap_keeps_recurring(self):
        """过期但问题仍在复现 → 保留。"""
        soul = self._write_soul_with_sections("writer", [
            ("ps-rec-0001", 20, r"零修改|无实质性", "## 自动优化规则\n\n逐条核对每个问题。\n"),
        ])
        reasons = [{"agent": "writer", "reason": "writer 又提交了与上一轮相同的文件，无实质性修改", "round_ref": ""}]
        reaped = self.po._reap_stale_auto_sections(reasons)
        self.assert_eq(reaped, 0, "复现中的问题段不应回收")
        after = soul.read_text(encoding="utf-8")
        self.assert_true("ps-rec-0001" in after, "段应保留")

    def _test_reap_keeps_fresh_and_foreign(self):
        """未过期段保留；pat='-'（非 score 来源）段即使过期也保留。"""
        soul = self._write_soul_with_sections("writer", [
            ("ps-fresh-01", 2, r"零修改", "## 自动优化规则\n\n新段。\n"),
            ("ps-foreign-1", 20, "-", "## 自动优化规则\n\nfailure_analyzer 来源段。\n"),
        ])
        reaped = self.po._reap_stale_auto_sections([])
        self.assert_eq(reaped, 0, "两类段都不应回收")
        after = soul.read_text(encoding="utf-8")
        self.assert_true("ps-fresh-01" in after and "ps-foreign-1" in after, "段应保留")

    def _test_reap_mixed(self):
        """混合场景：仅"过期+未复现+score来源"的段被回收。"""
        soul = self._write_soul_with_sections("critic", [
            ("ps-m-stale", 20, r"评分.*不一致", "## 自动优化规则\n\n评分自洽。\n"),
            ("ps-m-rec", 25, r"事实错误|基于错误.*前提", "## 自动优化规则\n\n先核实。\n"),
            ("ps-m-fresh", 1, r"超时", "## 自动优化规则\n\n限时。\n"),
        ])
        reasons = [{"agent": "critic", "reason": "critic 评审基于错误的事实前提", "round_ref": ""}]
        reaped = self.po._reap_stale_auto_sections(reasons)
        self.assert_eq(reaped, 1, "只应回收 stale 段")
        after = soul.read_text(encoding="utf-8")
        self.assert_true("ps-m-stale" not in after, "过期未复现段应删除")
        self.assert_true("ps-m-rec" in after, "复现段保留")
        self.assert_true("ps-m-fresh" in after, "新段保留")

    def _test_reap_creates_backup(self):
        """回收前自动备份到 prompt-backups/reap-*。"""
        self._write_soul_with_sections("writer", [
            ("ps-bk-0001", 20, r"零修改", "## 自动优化规则\n\n待回收。\n"),
        ])
        self.po._reap_stale_auto_sections([])
        baks = list(self.po.BACKUPS_DIR.glob("reap-writer-SOUL.md-*.bak"))
        self.assert_true(len(baks) >= 1, "应生成 reap 备份")


if __name__ == "__main__":
    suite = PromptBenchmarkGuardTests()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    import test_runner
    test_runner.print_report([suite])
    sys.exit(0 if suite.summary()["failed"] == 0 else 1)
