#!/usr/bin/env python3
"""
test_kb_distill_created_ts.py — 蒸馏页 created 时间戳回归测试

v6.9.7 修复验证:

kb_distill._ensure_source_raw 此前硬编码 now = "2026-08-15T00:00:00Z"。
蒸馏系统提示明确要求 LLM "直接输出 Markdown 正文（frontmatter 由系统补写）"，
即"无 frontmatter → 构造最小合规头"是主路径而非边缘分支——lc-kb-distill
cron（每日 12:50，5 篇/天）批量蒸馏后，全部新页的 created 字段冻结在
2026-08-15，后果:

1. KB 新鲜度指标（kb_health / KB 健康评分）基于 created/updated 计算，
   被冻结时间戳系统性污染；
2. growth_engine 生长阶段晋升依赖时间窗口，冻结 created 会让 seedling
   页面永远"当天创建"，晋升时序失真。

验证点:
    - 无 frontmatter 输出 → 构造头 created 可解析且与当前时间差 < 24h
    - 有 frontmatter 缺 source_raw → 补写 source_raw 不破坏 frontmatter 结构
"""

import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

TESTS_DIR = Path(__file__).parent
sys.path.insert(0, str(TESTS_DIR))
sys.path.insert(0, str(TESTS_DIR.parent))

from test_runner import TestSuite


class KbDistillCreatedTsTests(TestSuite):
    """kb_distill 蒸馏页 created 时间戳测试（零 LLM、零写入）。"""

    def __init__(self):
        super().__init__("kb_distill 蒸馏页 created 时间戳测试")

    def run_tests(self):
        import kb_distill

        # 1) 主路径：LLM 只输出正文 → 系统构造合规头，created 必须新鲜
        fresh = kb_distill._ensure_source_raw("正文内容", "x.md", "papers", "x")
        m = re.search(r'^created:\s*"?(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)"?',
                      fresh, re.M)
        if not self.assert_true(m is not None, "构造头包含 created 字段"):
            return
        try:
            ts = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%SZ") \
                .replace(tzinfo=timezone.utc)
            age = datetime.now(timezone.utc) - ts
            self.assert_true(
                abs(age) < timedelta(hours=24),
                "created 取真实当前时间（非冻结）",
                f"created={m.group(1)}，与当前相差 {abs(age)}",
            )
        except ValueError:
            self.assert_true(False, "created 可按 UTC ISO 解析", f"实际值 {m.group(1)!r}")

        # 2) 兼容路径：已有 frontmatter 缺 source_raw → 补写且结构不被破坏
        has_fm = "---\ntitle: y\ntype: papers\n---\n\n正文"
        fixed = kb_distill._ensure_source_raw(has_fm, "y.md", "papers", "y")
        self.assert_in('source_raw: "y.md"', fixed, "补写 source_raw（纯文件名）")
        self.assert_eq(fixed.count("---"), 2, "frontmatter 结构完整（两个定界符）")

        # 3) source_raw 注入位置在 frontmatter 内（首行 --- 之前不得出现正文级注入）
        self.assert_true(
            fixed.index('source_raw:') < fixed.index("正文"),
            "source_raw 注入在 frontmatter 内",
        )
