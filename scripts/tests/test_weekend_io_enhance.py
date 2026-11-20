#!/usr/bin/env python3
"""周末输入/输出优化测试（v6.10.12）。

输入端：assign_summaries borderline LLM 仲裁（跨术语语义归簇）
输出端：output_jobs._llm_json 委托加固版 + weekend_output 标签

用法：
    python3 scripts/self_test.py --module   # 自动发现
    python3 scripts/tests/test_weekend_io_enhance.py
"""

import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent.resolve()
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from test_runner import TestSuite


def _mk_cluster(cid="c1", title="Berry 曲率谱学", keywords=None):
    return {
        "cluster_id": cid, "title": title,
        # 4 关键词：重叠 1 → 0.7×1/4=0.175（borderline [0.12,0.22)）；
        # 重叠 3 → 0.525（> 0.22 走 Jaccard）——分母=簇侧是 _overlap 口径
        "keywords": keywords or ["berry曲率", "高次谐波", "谱学", "量子几何"],
        "summary": "研究 Berry 曲率在高次谐波谱学中的读出与反演。",
        "member_source_ids": [], "member_summaries": [],
        "status": "open", "linked_proposal_id": None,
        "created_at": "2026-09-01T00:00:00Z", "updated_at": "2026-09-01T00:00:00Z",
    }


def _mk_summary(sid="s1", title="量子度规的光学测量", summary="量子度规反演", keywords=None):
    return {
        "source_id": sid, "title": title, "summary": summary,
        "keywords": keywords or ["量子度规", "反演"],
    }


class WeekendIoEnhanceTests(TestSuite):
    def __init__(self):
        super().__init__("周末输入输出优化测试（v6.10.12）")

    def setup(self):
        pass

    def teardown(self):
        pass

    def run_tests(self):
        from weekend_pipeline import clusters as cl

        # ── 1. 高于阈值：原 Jaccard 路径不调 LLM ────────────────
        reg = {"clusters": [_mk_cluster()], "orphans": []}
        calls = []
        res = cl.assign_summaries(
            [_mk_summary(keywords=["berry曲率", "高次谐波", "谱学", "反演"])],
            reg, llm_arbiter=lambda *a: calls.append(1) or True)
        self.assert_eq(len(res["assigned"]), 1, "高相似应直接归入")
        self.assert_eq(len(calls), 0, "高相似不应调用 LLM")
        self.assert_true("method" not in res["assigned"][0], "Jaccard 路径无 method 标记")

        # ── 2. borderline + 仲裁 True → 归入（method=llm）────────
        reg = {"clusters": [_mk_cluster()], "orphans": []}
        # 词面重叠压到 ~0.17（borderline 区间 [0.12, 0.22)，实测校准）
        item = _mk_summary(keywords=["量子度规", "berry曲率", "反演", "光学", "测量", "压缩感知", "层析"])
        res = cl.assign_summaries([item], reg, llm_arbiter=lambda *a: True)
        self.assert_eq(len(res["assigned"]), 1, "borderline 仲裁 True 应归入")
        self.assert_eq(res["assigned"][0].get("method"), "llm", "应标记 llm")
        self.assert_eq(len(reg["clusters"][0]["member_source_ids"]), 1, "成员应入簇")

        # ── 3. borderline + 仲裁 False → orphan ─────────────────
        reg = {"clusters": [_mk_cluster()], "orphans": []}
        res = cl.assign_summaries([item], reg, llm_arbiter=lambda *a: False)
        self.assert_eq(len(res["assigned"]), 0, "仲裁 False 应 orphan")
        self.assert_eq(len(res["orphaned"]), 1, "应挂 orphan")

        # ── 4. 低于 borderline_low → 不调 LLM 直接 orphan ────────
        reg = {"clusters": [_mk_cluster()], "orphans": []}
        calls2 = []
        far = _mk_summary(sid="s2", keywords=["无线通信", "波束成形", "能效"])
        res = cl.assign_summaries([far], reg, llm_arbiter=lambda *a: calls2.append(1) or True)
        self.assert_eq(len(res["orphaned"]), 1, "低相似应 orphan")
        self.assert_eq(len(calls2), 0, "低相似不应浪费 LLM 调用")

        # ── 5. 仲裁异常 → 保守 orphan ───────────────────────────
        reg = {"clusters": [_mk_cluster()], "orphans": []}
        def _boom(*a): raise RuntimeError("llm down")
        res = cl.assign_summaries([item], reg, llm_arbiter=_boom)
        self.assert_eq(len(res["orphaned"]), 1, "仲裁异常应保守 orphan")

        # ── 6. 无 arbiter：纯 Jaccard 行为回归兼容 ──────────────
        reg = {"clusters": [_mk_cluster()], "orphans": []}
        res = cl.assign_summaries([item], reg)
        self.assert_eq(len(res["orphaned"]), 1, "无 arbiter 时 borderline 走 orphan（旧行为）")

        # ── 7. TASK_MAX_TOKENS 含 weekend_output ───────────────
        from llm_router import TASK_MAX_TOKENS
        self.assert_eq(TASK_MAX_TOKENS.get("weekend_output"), 16384,
                       "weekend_output 应放宽")
        self.assert_eq(TASK_MAX_TOKENS.get("weekend_input"), 16384,
                       "weekend_input 保持")

        # ── 8. output_jobs._llm_json 委托加固版（prefer 传递）──
        import weekend_pipeline.output_jobs as oj
        orig = None
        import weekend_pipeline.input_jobs as ij
        orig = ij._llm_json
        captured = {}
        try:
            def _fake(system, user, timeout=120, prefer=None):
                captured["prefer"] = prefer
                captured["timeout"] = timeout
                return {"ok": True}
            ij._llm_json = _fake
            r = oj._llm_json("s", "u", timeout=150)
            self.assert_eq(r, {"ok": True}, "委托应返回加固版结果")
            self.assert_eq(captured.get("prefer"), "weekend_output",
                           "应带 weekend_output 标签")
            self.assert_eq(captured.get("timeout"), 150, "timeout 应透传")
        finally:
            ij._llm_json = orig

        # ── 9. 萃取来源数 6→8 ───────────────────────────────────
        import inspect
        src = inspect.getsource(
            __import__("weekend_pipeline.output_jobs", fromlist=["x"])._extract_daily_knowledge)
        self.assert_true("sources[:8]" in src, "萃取来源应扩到 8 条")

        # ── 10. v7.3.64: 归档萃取 LLM 失败不再静默降级 ──────────
        # 背景：11-07 16:16/17:20 全 Provider 失败后 job 仍标 done 且
        # 萃取 0/0/0/0（假收敛）。修复后 _llm_json 返回 None 应诚实
        # 返回 success=False，交由 failed 重试通道自动重跑。
        import shutil as _sh
        from test_runner import create_isolated_env, patch_module_root, REAL_ROOT
        tmp = create_isolated_env()
        _orig_project_root = None
        try:
            for stage in ["drafts", "optimizing", "pending_review", "archived"]:
                (tmp / "research_proposals" / stage).mkdir(parents=True, exist_ok=True)
            prop = tmp / "research_proposals" / "optimizing" / "general-t-20260101"
            (prop / "04_proposal").mkdir(parents=True)
            (prop / "04_proposal" / "proposal-draft.md").write_text(
                "# 测试申请书\n\nBerry 曲率萃取测试内容。", encoding="utf-8")
            standards = REAL_ROOT / "memory" / "nsfc-standards.json"
            if standards.exists():
                _sh.copy(standards, tmp / "memory" / "nsfc-standards.json")
            for m in list(sys.modules):
                if m.startswith("weekend_pipeline") or m.startswith("proposal_lifecycle"):
                    del sys.modules[m]
            import paths
            _orig_project_root = paths.PROJECT_ROOT
            paths.PROJECT_ROOT = tmp
            import proposal_lifecycle.constants as plc
            plc.PROJECT_ROOT = tmp
            plc.PROPOSALS_ROOT = tmp / "research_proposals"
            patch_module_root("weekend_pipeline", tmp)
            patch_module_root("proposal_lifecycle", tmp)
            import weekend_pipeline.output_jobs as oj2
            _orig_llm, _orig_avail = oj2._llm_json, oj2.is_llm_available
            try:
                oj2.is_llm_available = lambda: True
                oj2._llm_json = lambda *a, **k: None
                r = oj2._extract_archived_proposal("general-t-20260101")
                self.assert_true(r.get("success") is False,
                                 "LLM 失败应诚实返回 success=False（不再假收敛）")
                self.assert_true("LLM" in r.get("error", ""),
                                 "错误信息应标明 LLM 失败原因")
                self.assert_true(r.get("archive_result", {}).get("success") is True,
                                 "归档产物结果应保留在返回值中")
            finally:
                oj2._llm_json, oj2.is_llm_available = _orig_llm, _orig_avail
        finally:
            if _orig_project_root is not None:
                paths.PROJECT_ROOT = _orig_project_root
            _sh.rmtree(tmp, ignore_errors=True)


def main() -> None:
    suite = WeekendIoEnhanceTests()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    ok = sum(1 for r in suite.results if r.passed)
    print(f"✓ {suite.name}: {ok}/{len(suite.results)} 通过")
    raise SystemExit(1 if len(suite.results) - ok else 0)


if __name__ == "__main__":
    main()
