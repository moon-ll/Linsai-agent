#!/usr/bin/env python3
"""
test_ghost_write_guard.py — 申请书产物幽灵写入与 cron stale 检测回归（v6.8.10-fix）

覆盖两个高置信度缺陷：

1. proposal_sections.assemble_draft() 在 sections/ 全部为空时禁止写入幽灵内容。
   触发场景：外部进程误清空 sections/、writer 失败后错误触发 assemble。
   期望：抛 ValueError 且 proposal-draft.md 不被覆盖。

2. lifecycle_monitor._check_cron_status() 必须能识别 hermes_bridge.cron_list()
   返回的真实字段 last_run（而不是错误的 last_run_at），避免 stale 检测永远命中空。

注意：本测试不调用 hermes/LLM，仅验证路径解析与字段兼容逻辑。
"""

import sys
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, REAL_ROOT


class GhostWriteGuardTests(TestSuite):
    def __init__(self):
        super().__init__("幽灵写入与 cron 字段兼容测试")
        self.tmp_root = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        (self.tmp_root / "research_proposals" / "drafts").mkdir(parents=True, exist_ok=True)
        (self.tmp_root / "research_proposals" / "optimizing").mkdir(parents=True, exist_ok=True)
        (self.tmp_root / "memory").mkdir(parents=True, exist_ok=True)
        # 复制真实 nsfc-standards.json（assemble_draft 可能引用）
        standards_src = REAL_ROOT / "memory" / "nsfc-standards.json"
        if standards_src.exists():
            import shutil
            shutil.copy(standards_src, self.tmp_root / "memory" / "nsfc-standards.json")

    def _test_assemble_draft_empty_sections_blocks(self):
        """v6.8.10-fix: sections/ 全空时 assemble_draft 必须抛 ValueError，禁止幽灵写入。"""
        from proposal_sections import ProposalSections

        prop_dir = self.tmp_root / "research_proposals" / "optimizing" / "general-test-ghost-20260101"
        sections_dir = prop_dir / "04_proposal" / "sections"
        sections_dir.mkdir(parents=True, exist_ok=True)
        draft = prop_dir / "04_proposal" / "proposal-draft.md"
        sentinel = "# sentinel\n\n已有 73KB 申请书占位，禁止被幽灵写入覆盖。\n" * 50
        draft.write_text(sentinel, encoding="utf-8")

        # v6.9.54 修正传参：ProposalSections 接受 04_proposal 目录本身
        # （sections_dir = proposal_dir/sections）。此前误传课题根目录，
        # draft_path 落在课题根 → sentinel 永远"不存在"，防护分支不可达
        ps = ProposalSections(prop_dir / "04_proposal")
        raised = False
        msg = ""
        try:
            ps.assemble_draft()
        except ValueError as e:
            raised = True
            msg = str(e)
        except Exception as e:
            self.assert_true(
                False,
                f"应抛 ValueError，实际抛 {type(e).__name__}: {e}",
            )

        self.assert_true(raised, "assemble_draft 在 sections/ 全空时必须抛 ValueError")
        self.assert_true(
            "拼接结果过小" in msg or "过小" in msg,
            f"ValueError 应包含'拼接结果过小'提示，实际: {msg}",
        )
        after = draft.read_text(encoding="utf-8")
        self.assert_eq(
            after, sentinel,
            "assemble_draft 抛错后 proposal-draft.md 必须保持原内容不被覆盖",
        )

    def _test_assemble_draft_normal_path_works(self):
        """回归守护：assemble_draft 在 sections/ 含正常内容时仍能正常写入。"""
        from proposal_sections import ProposalSections

        prop_dir = self.tmp_root / "research_proposals" / "optimizing" / "general-test-normal-20260101"
        sections_dir = prop_dir / "04_proposal" / "sections"
        sections_dir.mkdir(parents=True, exist_ok=True)
        # v6.9.54：样例扩到 >1KB（原样例约 100 字节，连自身断言的
        # >=1024 字节都不满足——该测试自写下以来从未真正运行过）
        para = (
            "强场超快光学以超短激光脉冲与物质相互作用为核心，近年来在阿秒时间尺度 "
            "的电子动力学观测方面取得一系列突破。本项目拟围绕多通道电离过程中的 "
            "相位恢复问题，发展兼具时间分辨与能量分辨的联合测量方案，并通过 TDDE "
            "数值模拟与解析理论相互印证，为下一代阿秒条纹相机提供物理基础。\n\n"
        )
        body = "## （一）立项依据\n\n" + para * 8
        (sections_dir / "rationale.md").write_text(body, encoding="utf-8")

        # v6.9.54 修正传参：同上，须传 04_proposal 目录
        ps = ProposalSections(prop_dir / "04_proposal")
        result = ps.assemble_draft()
        self.assert_true(result.exists(), "正常路径下 assemble_draft 必须返回有效路径")
        size = result.stat().st_size
        self.assert_true(
            size >= 1024,
            f"正常路径下 assemble_draft 输出应 >= 1024 字节，实际 {size}",
        )

    def _test_cron_stale_field_name_compat(self):
        """v6.8.10-fix: lifecycle_monitor 读取 last_run 应兼容 hermes_bridge 真实字段名。

        hermes_bridge.cron_list() 输出键名为 'last_run'（见 hermes_bridge.py:112）。
        lifecycle_monitor._check_cron_status() 先前误用 'last_run_at'，导致 stale
        检测永远拿到空字符串。修复后必须支持两种键名（last_run 优先）。
        """
        # 直接 monkey-patch hermes_bridge.cron_list_profile 返回 last_run（不 last_run_at）
        # v6.9.54 修复导入：scripts.lifecycle_monitor 需要"项目根"在 sys.path，
        # 而测试运行环境只保证 scripts/ 在 path——改用顶层导入（与其他测试一致）
        import lifecycle_monitor as lm_module

        # v6.9.54：_check_cron_status 先做拓扑对账（v6.8.54 起清单含 9 个固定
        # cron），样本必须补全清单，否则先触发 cron_missing 走不到 stale 分支。
        # lc-micro-scheduler 的 last_run 取 8h 前（动态），确保触发 stale。
        from datetime import datetime, timedelta, timezone
        iso = lambda dt: dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        now = datetime.now(timezone.utc)
        eight_h_ago = iso(now - timedelta(hours=8))
        now_iso = iso(now)

        def _cron(name, sched, last_run, **extra):
            d = {"name": name, "next_run": now_iso, "status": "active"}
            d.update(extra)
            d["schedule"] = sched
            if last_run is not None:
                d["last_run"] = last_run
            return d

        sample_crons = [
            _cron("lc-micro-scheduler", "*/5 * * * 1-5", eight_h_ago),
            # 兜底：旧键名 last_run_at 也应被识别（lc-hourly-monitor 用旧键名）
            _cron("lc-hourly-monitor", "0 * * * *", None, last_run_at=now_iso),
            _cron("lc-repair", "0 */12 * * *", now_iso),
            _cron("lc-daily-orchestrate", "55 8 * * *", now_iso),
            _cron("lc-prompt-optimize", "0 14 * * *", now_iso),
            _cron("lc-retrospective", "0 15 * * 1", now_iso),
            _cron("lc-kb-sync", "40 12 * * *", now_iso),
            _cron("lc-kb-distill", "50 12 * * *", now_iso),
            _cron("lc-daily-backup", "0 13 * * *", now_iso),
            _cron("lc-weekend-weekend-input", "0 9 * * 6", now_iso),
        ]

        captured = {}

        def fake_cron_list_profile(profile):
            captured["called_with"] = profile
            return sample_crons

        # 在脚本内 import 的是 hermes_bridge（绑定到 sys.modules 别名）
        import hermes_bridge as hb_real
        original = getattr(hb_real, "cron_list_profile", None)
        sys.modules["hermes_bridge"].cron_list_profile = fake_cron_list_profile
        try:
            result = lm_module._check_cron_status()
        finally:
            if original is not None:
                sys.modules["hermes_bridge"].cron_list_profile = original

        self.assert_eq(
            captured.get("called_with"), "linsai",
            "_check_cron_status 必须调用 cron_list_profile('linsai')",
        )
        # 关键断言：stale 检测必须能从 last_run 字段读到时间戳，
        # 即不能因为字段名错误返回 None 或抛异常。
        # lc-micro-scheduler 的 last_run 设为 8h 前，应被标记为 stale。
        if result is not None and result.get("type") == "cron_stale":
            stale = result.get("stale", [])
            names = [s.split(" (")[0] for s in stale]
            self.assert_true(
                "lc-micro-scheduler" in names,
                f"lc-micro-scheduler (last_run=8h 前，超过 stale 阈值) 必须被检测为 stale，实际: {stale}",
            )
        else:
            self.assert_true(
                False,
                f"修复后应返回 cron_stale 异常（lc-micro-scheduler 8h+ 未执行），实际: {result}",
            )

    def run_tests(self):
        self._test_assemble_draft_empty_sections_blocks()
        self._test_assemble_draft_normal_path_works()
        self._test_cron_stale_field_name_compat()


if __name__ == "__main__":
    suite = GhostWriteGuardTests()
    rc = suite.run()
    sys.exit(rc)