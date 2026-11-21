#!/usr/bin/env python3
"""test_retrospective_live.py — retrospective 活账本分析回归测试（v7.2.62）

背景（2026-10-30 确诊）：
    retrospective.py 原三个数据源中 memory/debug-journal.json 已死
    （2026-09-02 后零新增），连续数周报告输出「debug 条目总数：0」。
    v7.2.62 重建为活数据源：step_usage 月分片账本（LLM 调用）、
    research_proposals/_lifecycle.json（评分/未决问题/轮次）、
    CHANGELOG.md（BUG-Nn 速率）、system-kanban.json（执行事件）。

覆盖：
    1. step_usage 统计正确性（周期过滤/坏行跳过/失败分类/超时计数/TOP3）
    2. BUG 解析（版本头+编号、引入-修复间隔、velocity、坏日期行健壮）
    3. recurrence 缺字段兼容（无字段按 0 + missing_field_count + note 注明）
    4. cap 削幅计算（平均削幅/被 cap 判定/贴顶分布/覆盖率与 note）
    5. 机时经济学（周期轮次/活跃课题/日均/看板事件）
    6. 阈值触发（四项超限 ⚠ + 建议生成对齐格式）
    7. 缺文件/坏文件不崩（fail-open + warnings）
    8. 报告接入（活账本小节插在问题聚类之后 + 真实数据只读冒烟）

注意：
    仅验证纯逻辑（tempfile 构造迷你数据，零外部依赖、零 LLM、零写盘污染）。
"""

import json
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from test_runner import TestSuite

# 固定「当前时间」，让周期窗口（cutoff = now - 7d = 2026-10-23）完全确定
FIXED_NOW = datetime(2026, 10, 30, 12, 0, 0, tzinfo=timezone.utc)


def _write_usage_fixture(usage_dir: Path) -> None:
    """构造当月+上月 step_usage 分片。

    当月：周期内 3 条（1 成功 + 1 超时失败 + 1 限流失败）、周期外 1 条、坏行 1 条；
    上月：周期外 1 条（验证整分片被窗口过滤）。
    """
    usage_dir.mkdir(parents=True, exist_ok=True)
    rows = [
        {"ts": "2026-10-28T00:00:00Z", "kind": "llm_router", "name": "minimax",
         "success": True, "error": ""},
        {"ts": "2026-10-28T01:00:00Z", "kind": "llm_router", "name": "minimax",
         "success": False, "error": "✗ minimax: The read operation timed out"},
        {"ts": "2026-10-28T02:00:00Z", "kind": "hermes_agent", "name": "writer",
         "success": False, "error": "hermes agent 超时（30s）"},
        {"ts": "2026-09-05T00:00:00Z", "kind": "llm_router", "name": "glm",
         "success": False, "error": "✗ glm: 周期外老失败，不应计入"},
        "这行不是 JSON，应被跳过计数 parse_errors",
    ]
    (usage_dir / "step-usage-2026-10.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) if isinstance(r, dict) else r
                  for r in rows) + "\n",
        encoding="utf-8",
    )
    (usage_dir / "step-usage-2026-09.jsonl").write_text(
        json.dumps({"ts": "2026-09-05T00:00:00Z", "kind": "llm_router",
                    "name": "glm", "success": True}, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _lifecycle_fixture() -> Dict:
    """构造迷你 _lifecycle 数据（覆盖 recurrence 缺字段与 score_raw 有无）。"""
    return {"proposals": {
        "p1": {
            "score_history": [
                # 周期内，被 cap：0.80 → 0.75，贴 0.75 顶
                {"round": 1, "score": 0.75, "score_raw": 0.80,
                 "at": "2026-10-29T00:00:00Z"},
                # 周期内，无 score_raw（v7.2.62 前历史条目，跳过）
                {"round": 2, "score": 0.79, "at": "2026-10-29T06:00:00Z"},
                # 周期外（cap 为全量口径，仍计入）
                {"round": 3, "score": 0.60, "score_raw": 0.62,
                 "at": "2026-09-01T00:00:00Z"},
                # 周期内，削幅为 0 但 cap_applied=True（按标记计被 cap），贴 0.85 顶
                {"round": 4, "score": 0.85, "score_raw": 0.85,
                 "cap_applied": True, "at": "2026-10-28T00:00:00Z"},
            ],
            "open_critical_issues": [
                {"severity": "high", "description": "复发问题甲", "recurrence_count": 3},
                {"severity": "medium", "description": "历史问题乙（无 recurrence_count）"},
                {"severity": "high", "description": "字符串计数问题丙", "recurrence_count": "2"},
                {"severity": "low", "description": "空计数问题丁", "recurrence_count": None},
            ],
        },
        "p2": {
            "score_history": [
                # 周期内，削幅 0，贴 0.80 顶
                {"round": 1, "score": 0.80, "score_raw": 0.80,
                 "at": "2026-10-27T00:00:00Z"},
            ],
            "open_critical_issues": [
                {"severity": "medium", "description": "不复发问题戊", "recurrence_count": 0},
            ],
        },
    }}


def _write_changelog_fixture(path: Path) -> None:
    """构造 CHANGELOG（倒序，含 BUG 修复头/正文提及/坏日期行）。"""
    path.write_text(
        "# 变更记录\n"
        "\n"
        "## v7.2.62 - 2026-10-29 BUG-9 修复：演示修复头\n"
        "\n"
        "正文提到 BUG-10 的隐患（仅提及未修复，不计入修复数）。\n"
        "\n"
        "## v7.2.61 - 2026-10-20 隐患记录\n"
        "\n"
        "正文首次提到 BUG-9 的引入线索（早于修复 9 天）。\n"
        "\n"
        "## v7.2.60 - 2026-10-24 BUG-8 修复：窗口边缘的修复（10-24 ≥ cutoff 10-23）\n"
        "\n"
        "## v7.0.0 - 坏-日-期 版本头（应被健壮跳过，不计版本数）\n"
        "\n"
        "## v6.9.0 - 2026-03-01 远古版本（窗口外）\n",
        encoding="utf-8",
    )


def _write_kanban_fixture(path: Path) -> None:
    path.write_text(json.dumps({
        "execution_history": [
            {"at": "2026-10-29T08:00:00Z", "proposal_id": "p1",
             "step": "writer", "success": True},
            {"at": "2026-10-27T09:00:00Z", "proposal_id": "p2",
             "step": "critic", "success": False},
            {"at": "2026-09-05T00:00:00Z", "proposal_id": "p1",
             "step": "writer", "success": True},
        ],
    }, ensure_ascii=False), encoding="utf-8")


def _build_full_fixture(root: Path) -> Dict[str, Path]:
    """在 root 下搭一套完整迷你数据，返回各源路径。"""
    paths = {
        "usage_dir": root / "usage",
        "lifecycle": root / "_lifecycle.json",
        "changelog": root / "CHANGELOG.md",
        "kanban": root / "system-kanban.json",
    }
    _write_usage_fixture(paths["usage_dir"])
    paths["lifecycle"].write_text(
        json.dumps(_lifecycle_fixture(), ensure_ascii=False), encoding="utf-8")
    _write_changelog_fixture(paths["changelog"])
    _write_kanban_fixture(paths["kanban"])
    return paths


class RetrospectiveLiveTests(TestSuite):
    """retrospective 活账本分析（v7.2.62）回归测试。"""

    def __init__(self):
        super().__init__("retrospective 活账本分析测试")
        self.tmp = None
        self.paths = None

    def setup(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="linsai_retro_live_")
        self.paths = _build_full_fixture(Path(self.tmp.name))

    def teardown(self):
        if self.tmp:
            self.tmp.cleanup()

    def _analyze(self, **overrides):
        """带默认注入的分析入口。"""
        from retrospective import _analyze_live_ledgers
        kwargs = {
            "usage_dir": self.paths["usage_dir"],
            "lifecycle_path": self.paths["lifecycle"],
            "changelog_path": self.paths["changelog"],
            "kanban_path": self.paths["kanban"],
            "now": FIXED_NOW,
        }
        kwargs.update(overrides)
        return _analyze_live_ledgers(7, **kwargs)

    def run_tests(self):
        # ── 1. step_usage 统计正确性 ──
        live = self._analyze()
        ch = live["call_health"]
        self.assert_eq(ch["total_calls"], 3, "周期内调用总数（周期外 2 条被过滤）")
        self.assert_eq(ch["failed_calls"], 2, "失败数")
        self.assert_eq(ch["failure_rate"], 66.7, "失败率（2/3 四舍五入 66.7%）")
        self.assert_eq(ch["timeout_failures"], 2, "超时类失败（timed out + 超时（30s））")
        self.assert_eq(len(ch["top_failures"]), 2, "失败 TOP 组数")
        self.assert_true(
            ch["top_failures"][0]["error"] == "超时"
            and ch["top_failures"][0]["count"] >= 1,
            "TOP1 失败分类为超时")
        # 坏行产生 warning 但不崩溃
        self.assert_true(
            any("无法解析" in w for w in live["warnings"]),
            "坏行计入 parse_errors warning")
        from retrospective import _classify_usage_error
        self.assert_eq(_classify_usage_error("✗ glm: API HTTP 429: rate_limit_error"),
                       "HTTP 429 限流", "429 分类")
        self.assert_eq(_classify_usage_error(""), "未知错误", "空 error 分类")

        # ── 2. BUG 解析 ──
        bv = live["bug_velocity"]
        self.assert_eq(bv["bugs_fixed_in_period"], 2, "窗口内修复 BUG 数（BUG-8/9）")
        self.assert_eq(sorted(bv["bug_ids"]), ["8", "9"], "修复 BUG 编号")
        self.assert_eq(bv["bug_velocity_per_day"], 0.286, "bug_velocity = 2/7")
        # BUG-9 首见 10-20、修复 10-29 → 9 天；BUG-8 仅在修复头 → 0 天 → 均可考
        self.assert_eq(bv["interval_known"], 2, "引入-修复间隔可考数量")
        self.assert_eq(bv["avg_interval_days"], 4.5, "平均间隔 (9+0)/2")
        self.assert_eq(bv["versions_in_period"], 2, "窗口内版本数（坏日期行不计）")
        self.assert_eq(bv["versions_total"], 4, "总版本数（坏日期行不计）")

        # ── 3. recurrence 缺字段兼容 ──
        wa = live["whack_a_mole"]
        self.assert_eq(wa["total_issues"], 5, "open_critical_issues 总数")
        self.assert_eq(wa["recurrent_issues"], 2,
                       "复发数（甲=3 + 丙='2' 字符串；乙缺字段与丁=None 均按 0）")
        self.assert_eq(wa["rate_pct"], 40.0, "打地鼠率 2/5")
        self.assert_eq(wa["missing_field_count"], 1, "缺 recurrence_count 字段条数")
        self.assert_in("v7.2.62", wa["note"], "note 注明指标自 v7.2.62 起累积")
        self.assert_eq(wa["top_recurrences"][0]["count"], 3, "复发 TOP1 计数")

        # ── 4. cap 削幅计算 ──
        cs = live["cap_shaving"]
        self.assert_eq(cs["total_score_history"], 5, "score_history 总条数（全量口径）")
        self.assert_eq(cs["eligible"], 4, "含 score_raw 的可考条数")
        self.assert_eq(cs["coverage_pct"], 80.0, "覆盖率 4/5")
        # 削幅 = (0.05 + 0.02 + 0 + 0) / 4 = 0.0175
        self.assert_true(abs(cs["avg_shave"] - 0.0175) < 1e-9, "平均削幅 0.0175")
        # 被 cap：r1（削 0.05）+ r3（削 0.02）+ r4（cap_applied 标记）= 3
        self.assert_eq(cs["capped_count"], 3, "被 cap 条目数（含 cap_applied 标记）")
        self.assert_eq(cs["capped_ratio_pct"], 75.0, "被 cap 占比 3/4")
        self.assert_eq(cs["cap_hits"]["0.75"], 1, "贴顶 0.75 条数")
        self.assert_eq(cs["cap_hits"]["0.80"], 1, "贴顶 0.80 条数")
        self.assert_eq(cs["cap_hits"]["0.85"], 1, "贴顶 0.85 条数")
        self.assert_eq(cs["note"], "", "有可考条目时无需降级 note")

        # ── 5. 机时经济学 ──
        mh = live["machine_hours"]
        self.assert_eq(mh["rounds_in_period"], 4, "周期内新增评分轮次（09-01 排除）")
        self.assert_eq(mh["active_proposals"], 2, "活跃课题数")
        self.assert_eq(mh["daily_rounds"], 0.57, "日均轮次 4/7")
        self.assert_eq(mh["kanban_exec_events"], 2, "看板周期内执行事件")
        self.assert_eq(mh["kanban_active_proposals"], 2, "看板覆盖课题数")

        # ── 6. 阈值触发（构造四项全超限的数据）──
        warn_root = Path(self.tmp.name) / "warn"
        warn_root.mkdir()
        (warn_root / "usage").mkdir()
        # 失败率 100% > 15%
        (warn_root / "usage" / "step-usage-2026-10.jsonl").write_text(
            json.dumps({"ts": "2026-10-29T00:00:00Z", "kind": "llm_router",
                        "name": "minimax", "success": False,
                        "error": "✗ minimax: API HTTP 429"}, ensure_ascii=False) + "\n",
            encoding="utf-8")
        # 4 个 BUG 在 7 天窗口内修复（10-24~27 均 ≥ cutoff 10-23T12:00Z）→ 4/7 ≈ 0.571 > 0.5
        bug_headers = "\n".join(
            f"## v7.2.{60 + i} - 2026-10-2{i + 4} BUG-{i + 1} 修复：批量回归演示"
            for i in range(4))
        (warn_root / "CHANGELOG.md").write_text(
            f"# 变更记录\n\n{bug_headers}\n", encoding="utf-8")
        # 打地鼠率 100% + cap 削幅 0.10 > 0.02
        (warn_root / "_lifecycle.json").write_text(json.dumps({
            "proposals": {"pw": {
                "score_history": [
                    {"round": 1, "score": 0.70, "score_raw": 0.80,
                     "at": "2026-10-29T00:00:00Z"}],
                "open_critical_issues": [
                    {"severity": "high", "description": "全复发", "recurrence_count": 2}],
            }},
        }, ensure_ascii=False), encoding="utf-8")
        (warn_root / "system-kanban.json").write_text("{}", encoding="utf-8")

        from retrospective import (
            _analyze_live_ledgers,
            _format_live_section,
            _generate_action_suggestions,
        )
        live_warn = _analyze_live_ledgers(
            7, usage_dir=warn_root / "usage",
            lifecycle_path=warn_root / "_lifecycle.json",
            changelog_path=warn_root / "CHANGELOG.md",
            kanban_path=warn_root / "system-kanban.json", now=FIXED_NOW)
        warn_keys = {c["key"] for c in live_warn["thresholds"] if c["warn"]}
        self.assert_eq(
            warn_keys,
            {"call_fail_rate", "bug_velocity", "whack_rate", "cap_shave"},
            "四项阈值全部触发 ⚠")
        self.assert_true(
            abs(live_warn["bug_velocity"]["bug_velocity_per_day"] - 0.571) < 1e-9,
            "批量 BUG 修复 velocity 4/7")

        sec = _format_live_section(live_warn)
        self.assert_true(
            any(l.startswith("## 活账本指标（v7.2.62）") for l in sec),
            "小节标题正确")
        warn_lines = [l for l in sec if "⚠" in l]
        self.assert_true(len(warn_lines) >= 4, "四项 ⚠ 判定均出现在小节中")

        # 建议生成：每个 ⚠ 指标一条，格式对齐既有条目
        suggestions = _generate_action_suggestions(
            {"by_category": [], "top_tags": []}, {"details": []}, {},
            {"by_step": {}, "daily_breakdown": []}, live_warn)
        live_sugg = [s for s in suggestions if s["type"] == "活账本治理"]
        self.assert_eq(len(live_sugg), 4, "四条活账本治理建议")
        self.assert_true(
            all(s["priority"] == "high" and "category" in s and "description" in s
                for s in live_sugg),
            "建议条目字段与既有格式对齐")

        # ── 7. 缺文件/坏文件不崩 ──
        broken_root = Path(self.tmp.name) / "broken"
        broken_root.mkdir()
        (broken_root / "_lifecycle.json").write_text("{坏 JSON：并发写入窗口残片",
                                                     encoding="utf-8")
        live_broken = _analyze_live_ledgers(
            7, usage_dir=broken_root / "no-usage",
            lifecycle_path=broken_root / "_lifecycle.json",
            changelog_path=broken_root / "no-CHANGELOG.md",
            kanban_path=broken_root / "no-kanban.json", now=FIXED_NOW)
        self.assert_true(len(live_broken["warnings"]) >= 3,
                         "缺 usage/CHANGELOG/kanban + 坏 lifecycle 共 ≥3 条 warning")
        self.assert_eq(live_broken["call_health"]["total_calls"], 0,
                       "缺文件时调用统计为空结构")
        self.assert_eq(live_broken["whack_a_mole"]["total_issues"], 0,
                       "坏 lifecycle 时打地鼠为空结构")
        self.assert_eq(live_broken["machine_hours"]["rounds_in_period"], 0,
                       "坏 lifecycle 时机时为空结构")
        self.assert_no_exception(_format_live_section, "缺文件时格式化小节不崩",
                                 live_broken)
        # 无 proposals 的合法 lifecycle（空 dict 而非坏 JSON）
        (broken_root / "_lifecycle.json").write_text("{}", encoding="utf-8")
        live_empty = _analyze_live_ledgers(
            7, usage_dir=broken_root / "no-usage",
            lifecycle_path=broken_root / "_lifecycle.json",
            changelog_path=broken_root / "no-CHANGELOG.md",
            kanban_path=broken_root / "no-kanban.json", now=FIXED_NOW)
        self.assert_eq(live_empty["cap_shaving"]["note"], "",
                       "零条目时无降级 note（无数据 ≠ 有历史无新字段）")

        # ── 8. 报告接入 + 真实数据只读冒烟 ──
        from retrospective import _format_report
        report = _format_report(
            "7d", FIXED_NOW - timedelta(days=7),
            {"by_category": [], "top_tags": [], "total_filtered": 0},
            {"details": [], "total_tags_fixed": 0,
             "effective_count": 0, "ineffective_count": 0},
            {"writer": {}, "critic": {}},
            {"total_jobs": 0, "success_rate": 0, "daily_breakdown": [], "by_step": {}},
            [], [], None, live,
        )
        self.assert_in("## 活账本指标（v7.2.62）", report, "报告含活账本小节")
        self.assert_true(
            report.index("## 1. 问题聚类")
            < report.index("## 活账本指标（v7.2.62）")
            < report.index("## 2. 修复有效性"),
            "活账本小节位于问题聚类之后、修复有效性之前")
        # 真实数据冒烟（只读，验证对真实大文件/真实字段的健壮性）
        self.assert_no_exception(
            _analyze_live_ledgers, "真实数据只读分析不崩", 7)


if __name__ == "__main__":
    import time
    suite = RetrospectiveLiveTests()
    suite.setup()
    t0 = time.time()
    suite.run_tests()
    suite.teardown()
    suite.duration = time.time() - t0
    from test_runner import print_report
    print_report([suite])
