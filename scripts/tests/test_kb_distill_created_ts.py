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

        self.run_v6_9_15_tests()
        self.run_v6_9_75_tests()

    def run_v6_9_75_tests(self):
        """v6.9.75: agent_rejected 头读窗口回归（500B→8192B 修复验证）。

        v6.9.73 的 gate2 过滤器只读 raw 文件前 500 字节，而
        agent_rejected 在 frontmatter 字段序中位于 title/authors/
        agent_note 之后——大协作组论文（30+ 作者）该行偏移 660B+，
        溢出窗口致被拒论文漏检、仍进蒸馏队列浪费 LLM 配额。
        """
        import json
        import tempfile
        import kb_distill
        import kb_index

        def _mk_frontmatter(n_authors: int, rejected: bool) -> str:
            authors = ", ".join(f"Author Name {i:03d}" for i in range(n_authors))
            note = "强场相关，方向匹配，建议入池跟踪"
            return "\n".join([
                "---",
                'title: "Topological photonics in twisted van der Waals heterostructures"',
                'arxiv_id: "2608.99999"',
                f'authors: "{authors}"',
                'year: "2026"',
                'tags: ["deepxiv-论文库"]',
                'direction: "阿秒科学"',
                'source: "hermes-简报"',
                'imported_at: "2026-08-28T10:28:20Z"',
                "score_deepxiv: 0.62",
                f"score_agent: {json.dumps(2 if rejected else 7)}",
                f'agent_note: "{note}"',
                f"agent_rejected: {json.dumps(rejected)}",
                'abstract: "placeholder"',
                "---", "",
                "# 正文",
            ])

        tmpdir = tempfile.mkdtemp(prefix="kb_distill_win_")
        kd_dir = Path(tmpdir)
        (kd_dir / "raw" / "papers").mkdir(parents=True)
        # 40 作者 → agent_rejected 偏移约 850B（500B 窗口外、8192B 内）
        rejected_md = _mk_frontmatter(40, rejected=True)
        (kd_dir / "raw" / "papers" / "a-rejected.md").write_text(rejected_md, encoding="utf-8")
        off = rejected_md.find("agent_rejected: true")
        if not self.assert_true(off > 500, "构造用例偏移确实落在旧 500B 窗口之外",
                                f"实际偏移 {off}B"):
            return
        (kd_dir / "raw" / "papers" / "b-accepted.md").write_text(
            _mk_frontmatter(40, rejected=False), encoding="utf-8")

        orig = (kb_distill.KNOWLEDGE_DIR, kb_distill._wiki_source_raws,
                kb_distill._is_excluded, kb_index.list_raw_files)
        try:
            kb_distill.KNOWLEDGE_DIR = kd_dir
            kb_distill._wiki_source_raws = lambda: set()
            kb_distill._is_excluded = lambda p: False
            kb_index.list_raw_files = lambda: [
                {"name": "b-accepted.md", "path": "raw/papers/b-accepted.md", "mtime": 1},
                {"name": "a-rejected.md", "path": "raw/papers/a-rejected.md", "mtime": 2},
            ]
            out = kb_distill.pending_distill_list()
            names = [p.name for p in out]
            self.assert_true("a-rejected.md" not in names,
                             "大作者列表下 agent_rejected=true 仍被过滤（8192B 窗口）",
                             f"实际清单 {names}")
            self.assert_in("b-accepted.md", names, "未被拒论文正常进入蒸馏队列")
        finally:
            (kb_distill.KNOWLEDGE_DIR, kb_distill._wiki_source_raws,
             kb_distill._is_excluded, kb_index.list_raw_files) = orig

    def run_v6_9_15_tests(self):
        """v6.9.15: distill_one 传 prefer=kb_distill（GLM 主模型路由）。"""
        import kb_distill

        captured = {}
        orig = (
            kb_distill.distill_raw_to_wiki,
            kb_distill.save_distilled_wiki,
        )
        import llm_gateway
        orig_gw = llm_gateway.llm_complete
        # v6.9.16 修复：distill_one 首行对 raw_path 做 relative_to(KNOWLEDGE_DIR)，
        # "/tmp/fake/raw/x.md" 不在任何隔离 KNOWLEDGE_DIR 下必然 ValueError，
        # 该回归自 v6.9.15 落地起整套件被 self_test 静默吞掉、从未真正运行。
        orig_kd = kb_distill.KNOWLEDGE_DIR
        # v6.9.75 加固：distill_one 现会读取 raw 全文（分层蒸馏判定
        # has_fulltext 前 1200B），此前用例依赖 /tmp 残留文件、净环境
        # （新沙箱/清理后）必挂 FileNotFoundError——改为用例自建自清
        fake_raw = Path("/tmp/fake/raw/x.md")
        try:
            kb_distill.KNOWLEDGE_DIR = Path("/tmp/fake")
            fake_raw.parent.mkdir(parents=True, exist_ok=True)
            fake_raw.write_text("---\ntitle: x\n---\n\n正文", encoding="utf-8")
            kb_distill.distill_raw_to_wiki = lambda rel: ("wiki/x.md", "prompt")
            kb_distill.save_distilled_wiki = lambda *a, **k: None
            llm_gateway.llm_complete = (
                lambda sys_p, usr_p, timeout=90, prefer=None: (
                    captured.update(prefer=prefer) or (True, "# 标题\n正文", {"provider": "glm"})
                )
            )
            r = kb_distill.distill_one(Path("/tmp/fake/raw/x.md"))
            self.assert_true(r.get("success"), "stub 蒸馏应成功", str(r))
            self.assert_eq(
                captured.get("prefer"), "kb_distill",
                "distill_one 应传 prefer=kb_distill（GLM 主模型）",
            )
        finally:
            kb_distill.distill_raw_to_wiki, kb_distill.save_distilled_wiki = orig
            llm_gateway.llm_complete = orig_gw
            kb_distill.KNOWLEDGE_DIR = orig_kd
            fake_raw.unlink(missing_ok=True)
