#!/usr/bin/env python3
"""
test_gap_json_repair.py — gap_identify JSON 引号修复回归测试（v6.10.6）

覆盖两类修复：
    1. _repair_json_inner_quotes：字符串内未转义 ASCII 引号修复
       （2026-09-10 bsv r2 scheme 实例：claim 嵌套引号致 2859 字有效
       输出被静默丢弃，下游 lit 链空转触发 api_idle_spin 告警）
    2. health_sensor LOCAL_FAST_STEPS：纯本地步骤（lit_note）不计数
       空转（lit_note 实测 ~1s：regex 抽取 + 本地关联，秒级是正常行为）

注意：
    本测试不调用 hermes/LLM，仅验证解析与扫描的数据逻辑。

用法示例：
    python3 scripts/tests/test_gap_json_repair.py
"""

import json
import sys
from datetime import datetime, timedelta, timezone

from test_runner import TestSuite, create_isolated_env


class GapJsonRepairTests(TestSuite):
    def __init__(self):
        super().__init__("gap_identify JSON 引号修复测试")
        self._repair = None
        self._sensor = None

    def setup(self):
        create_isolated_env()
        from lifecycle.executor import _repair_json_inner_quotes
        import health_sensor

        self._repair = _repair_json_inner_quotes
        self._sensor = health_sensor

    def teardown(self):
        pass

    def run_tests(self):
        repair = self._repair

        # ---------- 1. 复刻翻车实例：claim 内嵌未转义 ASCII 引号 ----------
        broken = (
            '{"gaps": [{"claim": "BSV-HHG探针的可行性需要单独论证"光源—样品—谱学'
            '—理论—反演"五环中每一环的原理可证伪性", "missing_evidence": "缺少文献", '
            '"search_keywords": ["BSV HHG"], "priority": "high"}]}'
        )
        try:
            json.loads(broken)
            self.assert_true(False, "原始非法 JSON 不应直接解析成功")
        except json.JSONDecodeError:
            pass
        repaired = json.loads(repair(broken))
        self.assert_eq(len(repaired["gaps"]), 1, "修复后解析出 1 条缺口")
        self.assert_true(
            '论证"光源—样品—谱学—理论—反演"五环' in repaired["gaps"][0]["claim"],
            "claim 内容完整保留（引号原样在内）",
        )

        # ---------- 2. 多处内嵌引号 + 多条 gaps ----------
        broken2 = (
            '{"gaps": [{"claim": "甲"乙"丙", "missing_evidence": "m1"}, '
            '{"claim": "丁"戊"己", "missing_evidence": "m2"}]}'
        )
        repaired2 = json.loads(repair(broken2))
        self.assert_eq(len(repaired2["gaps"]), 2, "多条 gaps 均修复")

        # ---------- 3. 正常 JSON 不被改动 ----------
        ok = '{"gaps": [{"claim": "正常文本（§3.5）", "priority": "high"}], "note": "x"}'
        self.assert_eq(repair(ok), ok, "正常 JSON 原样返回")

        # ---------- 4. 已转义引号不重复转义 ----------
        esc = '{"k": "a\\"b", "j": 1}'
        self.assert_eq(
            json.loads(repair(esc)), json.loads(esc), "已转义引号保持等价"
        )

        # ---------- 5. 空字符串与嵌套结构 ----------
        edge = '{"a": "", "b": [{"c": "x"}, {"d": 2}], "e": null}'
        self.assert_eq(json.loads(repair(edge)), json.loads(edge), "空串/嵌套/null 等价")

        # ---------- 6. 键名后的冒号结构不受影响 ----------
        struct = '{"gaps": [], "note": "尾部说明"}'
        self.assert_eq(json.loads(repair(struct)), json.loads(struct), "空 gaps 结构等价")

        # ---------- 7. lit_note 本地步骤不计入空转 ----------
        sensor = self._sensor
        now = datetime.now(timezone.utc)
        started = (now - timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        finished = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        jobs = [
            {
                "job_id": "p-r1-scheme-lit_note",
                "step": "lit_note",
                "status": "done",
                "started_at": started,
                "finished_at": finished,
            },
            {
                "job_id": "p-r1-scheme-lit_search",
                "step": "lit_search",
                "status": "done",
                "started_at": started,
                "finished_at": finished,
            },
        ]
        scan = sensor._scan_proposal_jobs(jobs, now)
        self.assert_eq(
            scan["idle_jobs"],
            ["p-r1-scheme-lit_search"],
            "lit_note 被排除，lit_search 仍计入空转",
        )

        # ---------- 8. 旧 job 无 step 字段仍计数（向后兼容） ----------
        legacy = [{
            "job_id": "p-r1-old-job",
            "status": "done",
            "started_at": started,
            "finished_at": finished,
        }]
        scan2 = sensor._scan_proposal_jobs(legacy, now)
        self.assert_eq(scan2["idle_jobs"], ["p-r1-old-job"], "无 step 字段 job 保持计数")


def main() -> None:
    suite = GapJsonRepairTests()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    ok = sum(1 for r in suite.results if r.passed)
    print(f"✓ {suite.name}: {ok}/{len(suite.results)} 通过")
    raise SystemExit(1 if len(suite.results) - ok else 0)


if __name__ == "__main__":
    main()
