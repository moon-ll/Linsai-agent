# -*- coding: utf-8 -*-
"""课题启动包管线（v8）——CLI 命令行入口。

用法示例：
    python3 scripts/topic_pipeline.py --register --title "..." --problem "..." --slug "..."
    python3 scripts/topic_pipeline.py --daily                     # 每日深研 worker
    python3 scripts/topic_pipeline.py --deep-dive <topic_id>      # 手动深研
    python3 scripts/topic_pipeline.py --assemble <topic_id>       # 手动组装
    python3 scripts/topic_pipeline.py --check <topic_id>          # 验收自检
    python3 scripts/topic_pipeline.py --check-all                 # 全量自检
    python3 scripts/topic_pipeline.py --activate <topic_id>       # 人工启动（ready→active）
    python3 scripts/topic_pipeline.py --reject <topic_id> --reason "..."
    python3 scripts/topic_pipeline.py --archive <topic_id>        # 收尾归档
    python3 scripts/topic_pipeline.py --migrate-v7 [--dry-run]    # v7 存量迁移
    python3 scripts/topic_pipeline.py --list                      # 看板
    python3 scripts/topic_pipeline.py --setup-cron                # 安装 v8 cron
    python3 scripts/topic_pipeline.py --self-check                # 模块自检
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from . import acceptance, assemble, deep_research, migration, registration, state  # noqa: E402
from .card import STAGE_LABELS  # noqa: E402
from .constants import STAGES, TOPICS_ROOT  # noqa: E402


def _print_board() -> int:
    data = state.load_state()
    topics = data.get("topics", {})
    if not topics:
        print("○ 课题库为空（research_topics/ 尚无登记课题）")
        return 0
    print(f"林赛研究工作台 · 课题看板（共 {len(topics)} 个，状态即目录）")
    for stage in STAGES:
        ids = [tid for tid, rec in sorted(topics.items())
               if isinstance(rec, dict) and rec.get("stage") == stage]
        if not ids:
            continue
        print(f"\n[{stage}] {STAGE_LABELS.get(stage, stage)}（{len(ids)}）")
        for tid in ids:
            rec = topics[tid]
            marks = []
            if rec.get("needs_human"):
                marks.append("⚠等人")
            if rec.get("deep_dive_gaps"):
                marks.append("◐缺口:" + ",".join(rec["deep_dive_gaps"]))
            print(f"  - {tid}  {rec.get('title', '')}  {' '.join(marks)}")
    rej = data.get("rejected", {})
    if rej:
        print(f"\n[_rejected] 否决台账（{len(rej)}）")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="课题启动包管线（v8 工作台）")
    ap.add_argument("--register", action="store_true", help="注册问题候选")
    ap.add_argument("--title", default="")
    ap.add_argument("--problem", default="")
    ap.add_argument("--source", default="manual")
    ap.add_argument("--slug", default="")
    ap.add_argument("--card-file", default="", help="知识卡摘要文件路径")
    ap.add_argument("--related", default="", help="关联课题 ID，逗号分隔")
    ap.add_argument("--force", action="store_true", help="跳过新颖性硬门（慎用）")
    ap.add_argument("--daily", action="store_true", help="每日深研 worker")
    ap.add_argument("--deep-dive", default="", metavar="TOPIC_ID")
    ap.add_argument("--steps", default="", help="深研步骤子集，逗号分隔（background,problem,scheme）")
    ap.add_argument("--assemble", default="", metavar="TOPIC_ID")
    ap.add_argument("--check", default="", metavar="TOPIC_ID")
    ap.add_argument("--check-all", action="store_true")
    ap.add_argument("--activate", default="", metavar="TOPIC_ID", help="人工启动 ready→active")
    ap.add_argument("--reject", default="", metavar="TOPIC_ID")
    ap.add_argument("--reject-reason", default="")
    ap.add_argument("--archive", default="", metavar="TOPIC_ID")
    ap.add_argument("--migrate-v7", action="store_true")
    ap.add_argument("--only", default="", help="迁移限定单个课题 ID")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--setup-cron", action="store_true")
    ap.add_argument("--teardown-cron", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args(argv)

    # ------------------------------------------------ 自检
    if args.self_check:
        return _self_check()

    # ------------------------------------------------ 注册
    if args.register:
        card = ""
        if args.card_file and Path(args.card_file).exists():
            card = Path(args.card_file).read_text(encoding="utf-8")
        res = registration.register_question(
            title=args.title, problem=args.problem, source=args.source,
            slug=args.slug, knowledge_card=card,
            related=[x.strip() for x in args.related.split(",") if x.strip()],
            force=args.force, dry_run=args.dry_run,
        )
        print(("✓ " if res.get("registered") else "✗ ") + str(res.get("reason") or res.get("topic_id")))
        if res.get("registered"):
            print(f"  课题目录: {res['dir']}（新颖性 {res['novelty']['max_score']}）")
            return 0
        return 0 if res.get("dry_run") else 1

    # ------------------------------------------------ 每日 worker
    if args.daily:
        from .daily import run_daily
        res = run_daily(dry_run=args.dry_run)
        print("✓" if res.get("success") else "✗", res.get("summary") or res.get("skipped") or res.get("error", ""))
        for r in res.get("results", []):
            print(f"  ◐ {r['topic_id']} 深研gaps={r['deep_dive'].get('gaps', [])}")
        return 0

    # ------------------------------------------------ 深研
    if args.deep_dive:
        steps = [s.strip() for s in args.steps.split(",") if s.strip()] or None
        res = deep_research.deep_dive(args.deep_dive, steps=steps, dry_run=args.dry_run)
        if not res.get("success") and res.get("error"):
            print("✗", res["error"])
            return 1
        print(("✓ " if res.get("success") else "◐ ") + f"深研完成度: {len([s for s in res['steps_run'] if s.get('success')])}/{len(res['steps_run'])}")
        for s in res["steps_run"]:
            print(f"  - {s.get('step')}: {'✓' if s.get('success') or s.get('skipped') or s.get('dry_run') else '✗ ' + str(s.get('error', ''))}")
        if res.get("gaps"):
            print("  缺口（下次深研补齐）:", ",".join(res["gaps"]))
        return 0 if res.get("success") else 1

    # ------------------------------------------------ 组装
    if args.assemble:
        res = assemble.assemble_report(args.assemble, dry_run=args.dry_run)
        if not res.get("success"):
            print("✗", res.get("error"))
            return 1
        print(f"✓ 报告 {res.get('report_chars', 0)} 字符（G1 上限 {'超出' if res.get('over_limit') else '未超'}）",
              res.get("report", ""))
        return 0

    # ------------------------------------------------ 验收自检
    if args.check:
        res = acceptance.check_topic(args.check, dry_run=args.dry_run)
        if not res.get("success"):
            print("✗", res.get("error"))
            return 1
        v = res["verdict"]
        icon = "✓" if v["passed"] else "✗"
        print(f"{icon} {args.check} 验收自检：{'全过' if v['passed'] else str(len(v['gaps'])) + ' 项缺口'}")
        for r in v["results"]:
            print(f"  {'✓' if r['passed'] else '✗'} {r['code']} {r['name']}  {r['evidence']}")
        if v["gaps"]:
            print("  缺口:", "；".join(v["gaps"]))
        return 0 if v["passed"] else 1
    if args.check_all:
        data = state.load_state()
        ids = state.list_by_stage(data, "kickoff") + state.list_by_stage(data, "ready")
        rc = 0
        for tid in ids:
            if acceptance.check_topic(tid).get("verdict", {}).get("passed"):
                print(f"✓ {tid}")
            else:
                print(f"◐ {tid} 有缺口")
                rc = 1
        if not ids:
            print("○ 无 kickoff/ready 课题")
        return rc

    # ------------------------------------------------ 人工节点
    if args.activate:
        data = state.load_state()
        rec = state.get_topic(data, args.activate)
        if not rec:
            print("✗ 课题不存在:", args.activate)
            return 1
        if rec.get("stage") not in ("ready", "questions", "kickoff"):
            print("✗ 仅 ready（或人工裁量 questions/kickoff）可启动，当前:", rec.get("stage"))
            return 1
        # v8.0.1：transition 统一入口（状态 + 目录搬移一致）
        moved = state.transition(args.activate, "active", "人工立项启动（工作台）")
        tdir = moved.get("dir") or state.topic_dir(args.activate)
        if tdir:
            from .card import append_card_event
            append_card_event(Path(tdir) / "topic-card.md", f"{state._now()} → active（人工立项启动）")
        print("✓ 已启动（active）:", args.activate, "——正式研究开始，建议同步 task_manager 建任务")
        return 0
    if args.reject:
        with state.state_lock():
            data = state.load_state()
            state.reject_topic(data, args.reject, args.reject_reason or "（未填写理由）")
            state.save_state(data)
        # v8.0.1：任意阶段目录 → _rejected-questions/（不再假设 questions）
        state.move_to_rejected(args.reject)
        print("✓ 已否决:", args.reject, "理由:", args.reject_reason or "（未填写）")
        return 0
    if args.archive:
        # v8.0.1：transition 统一入口（状态 + 目录搬移一致）
        state.transition(args.archive, "archive", "收尾归档（人工）")
        print("✓ 已归档:", args.archive)
        return 0

    # ------------------------------------------------ 迁移
    if args.migrate_v7:
        res = migration.migrate_v7(dry_run=args.dry_run, only=args.only or None)
        head = "预览" if args.dry_run else "完成"
        print(f"✓ v7→v8 迁移{head}：{res['count']} 个课题"
              + (f"，否决台账 {res.get('rejected_migrated', 0)} 条" if not args.dry_run else ""))
        for r in res.get("results", []):
            if r.get("error"):
                print("  ✗", r["topic_id"], r["error"])
            elif r.get("skipped"):
                print("  ○", r["topic_id"], r["skipped"])
            else:
                print("  ✓", r["topic_id"], "→", r.get("stage_v8", "?"))
        return 0

    # ------------------------------------------------ cron
    if args.setup_cron:
        from .cron import setup_cron
        res = setup_cron()
        for j in res.get("jobs", []):
            print(("✓ " if j["success"] else "✗ ") + f"{j['name']} {j['schedule']}")
        return 0 if res.get("success") else 1
    if args.teardown_cron:
        from .cron import teardown_cron
        res = teardown_cron()
        print("✓ 已移除:", ",".join(res.get("removed", [])))
        return 0

    # ------------------------------------------------ 看板
    if args.list:
        return _print_board()

    print("○ 未指定操作（--help 查看全部命令）")
    return 0


def _self_check() -> int:
    """模块自检：包导入 + 核心函数可调用 + 目录结构约定。"""
    from . import similarity  # noqa: F401
    from .card import parse_card, render_card  # noqa: F401
    from .constants import A2_NOVELTY_THRESHOLD, STAGES
    assert STAGES == ("questions", "kickoff", "ready", "active", "archive")
    assert similarity.jaccard_similarity("固体高次谐波", ["固体高次谐波调控"]) >= 0.3
    assert similarity.jaccard_similarity("量子计算", ["拓扑声学"]) < 0.3
    card = render_card("t", "general-t-20260101", "questions", problem="p")
    assert "课题卡" in card and "questions" in card
    print("✓ topic_pipeline 自检通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
