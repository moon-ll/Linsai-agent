#!/usr/bin/env python3
"""test_weekend_kb_maintain.py — 知识库深度维护回归测试（v6.9.6）

覆盖：
    1. 周末反思阶段新 job（reflection_kb_deep_health / reflection_kb_merge_duplicates）
       的模板定义、依赖关系。
    2. kb_merger 纯函数：related 边合并去重、选主逻辑、stub 生成、降级正文。
    3. kb_taxonomy tag 清洗：# 前缀/纯标点/过短 tag 排除。

注意：
    本测试不调用 LLM、不写入知识库，仅验证纯逻辑。
"""

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from test_runner import TestSuite


class WeekendKbMaintainTests(TestSuite):
    def __init__(self):
        super().__init__("知识库深度维护测试（v6.9.6）")

    def run_tests(self):
        from weekend_pipeline.jobs import reflection_stage_jobs

        # ================================================================
        # 测试 1: 反思阶段模板含两个新 KB 维护 job，且依赖正确
        # ================================================================
        jobs = {j["job_id"]: j for j in reflection_stage_jobs()}
        self.assert_true(
            "reflection_kb_deep_health" in jobs, "缺 reflection_kb_deep_health job"
        )
        self.assert_true(
            "reflection_kb_merge_duplicates" in jobs, "缺 reflection_kb_merge_duplicates job"
        )
        self.assert_eq(
            jobs["reflection_kb_deep_health"].get("depends_on"), [],
            "deep_health 应无依赖（与反思链并行）"
        )
        self.assert_eq(
            jobs["reflection_kb_merge_duplicates"].get("depends_on"),
            ["reflection_kb_deep_health"],
            "merge 应依赖 deep_health（先检测后合并）"
        )

        # ================================================================
        # 测试 2: 新 job 模板自动合并进已有 state（run_stage 行为模拟）
        # ================================================================
        existing = [
            {"job_id": "reflection_health_check", "status": "done"},
            {"job_id": "reflection_collect_state", "status": "pending"},
        ]
        template_ids = [j["job_id"] for j in reflection_stage_jobs()]
        existing_ids = [j["job_id"] for j in existing]
        for j in reflection_stage_jobs():
            if j["job_id"] not in existing_ids:
                existing.append(j)
        merged_ids = [j["job_id"] for j in existing]
        self.assert_true("reflection_kb_deep_health" in merged_ids, "新 job 未被合并进 state")
        self.assert_eq(len(existing), len(template_ids), "合并后 job 数应与模板一致")

        # ================================================================
        # 测试 3: kb_merger related 合并——并集去重 + 剔除互指/自指
        # ================================================================
        from kb_merger import merge_related
        r = merge_related(
            ["高频谐波", "阿秒物理"],
            ["阿秒物理", "强场物理", "高频谐波", "固体物理"],
            "高频谐波", "固体物理",
        )
        self.assert_eq(r, ["阿秒物理", "强场物理"], "related 合并结果异常")
        self.assert_true("固体物理" not in r, "被并页标题（互指）应剔除")
        self.assert_true("高频谐波" not in r, "主页面标题（自指）应剔除")

        # ================================================================
        # 测试 4: kb_merger 选主——正文长者优先，同长比 updated_at 新者
        # ================================================================
        from kb_merger import pick_primary
        fake = {
            "a.md": {"frontmatter": {"title": "短", "updated_at": "2026-08-15T00:00:00Z"}, "body": "x" * 10},
            "b.md": {"frontmatter": {"title": "长", "updated_at": "2026-08-01T00:00:00Z"}, "body": "x" * 100},
        }
        self.assert_eq(pick_primary(["a.md", "b.md"], lambda p: fake.get(p)), "b.md", "正文长者应为主页面")
        fake2 = {
            "a.md": {"frontmatter": {"title": "同长旧", "updated_at": "2026-08-01T00:00:00Z"}, "body": "x" * 50},
            "b.md": {"frontmatter": {"title": "同长新", "updated_at": "2026-08-15T00:00:00Z"}, "body": "x" * 50},
        }
        self.assert_eq(pick_primary(["a.md", "b.md"], lambda p: fake2.get(p)), "b.md", "同长时 updated_at 新者为主")

        # ================================================================
        # 测试 5: kb_merger stub 正文与 LLM 失败降级正文
        # ================================================================
        from kb_merger import build_stub_body, _fallback_body
        s = build_stub_body("旧概念", "新概念", "wiki/concepts/x.md")
        self.assert_true("已合并" in s and "wiki/concepts/x.md" in s, "stub 缺主页面指向")
        fb = _fallback_body("主体内容", "被并内容", "被并页")
        self.assert_true("主体内容" in fb and "合并自「被并页」" in fb and "被并内容" in fb, "降级正文附录并置异常")

        # ================================================================
        # 测试 6: kb_taxonomy tag 清洗——垃圾 tag 全排除
        # ================================================================
        from kb_taxonomy import _clean_tag
        for bad in ["#", "#type/concept", "\\", '"', ",", "", " ", "---", "ab", "概"]:
            self.assert_true(not _clean_tag(bad), "垃圾 tag 应被排除: %r" % bad)
        for good in ["强场超快", "NSFC", "attosecond", "相位匹配"]:
            self.assert_true(_clean_tag(good), "正常 tag 应保留: %r" % good)


if __name__ == "__main__":
    suite = WeekendKbMaintainTests()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    import test_runner
    test_runner.print_summary([suite])
    sys.exit(0 if suite.failed == 0 else 1)
