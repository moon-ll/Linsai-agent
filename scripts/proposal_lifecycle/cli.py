from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional

from proposal_lifecycle import (
    LIFECYCLE_STAGES,
    PROJECT_TYPES,
    ProposalLifecycle,
)


def _update_kanban_task_sync(ctrl) -> None:
    """更新看板中的 task_sync 字段，在 CLI 同步任务后调用。"""
    try:
        from common import load_json, save_json, now_utc
        from paths import PROJECT_ROOT
        kanban_path = PROJECT_ROOT / "memory" / "system-kanban.json"
        if not kanban_path.exists():
            return
        kanban = load_json(kanban_path, default={})
        # 收集 task_manager 统计
        try:
            import task_manager as tm
            all_tasks = tm.list_tasks()
            task_stats = {
                "total": len(all_tasks),
                "backlog": sum(1 for t in all_tasks if t.get("status") == "backlog"),
                "active": sum(1 for t in all_tasks if t.get("status") == "active"),
                "completed": sum(1 for t in all_tasks if t.get("status") == "completed"),
                "lifecycle_tasks": sum(1 for t in all_tasks if t.get("title", "").startswith("「优化」")),
            }
        except Exception:
            task_stats = {}
        # 从 lifecycle 映射获取映射数量
        try:
            from lifecycle.micro_scheduler import _load_lifecycle_task_map
            mapping_count = len(_load_lifecycle_task_map())
        except Exception:
            mapping_count = 0
        kanban["task_sync"] = {
            "enabled": True,
            "stats": task_stats,
            "mapping_count": mapping_count,
            "last_sync_at": now_utc(),
        }
        save_json(kanban_path, kanban)
    except Exception:
        pass


def main(argv: Optional[List[str]] = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="提案生命周期管理")
    parser.add_argument("--dashboard", action="store_true", help="显示仪表盘")
    parser.add_argument("--list", metavar="STATUS", help="按状态列出 proposal")
    parser.add_argument("--register", nargs="+", metavar=("ID", "TYPE"),
                        help="注册新 proposal（--register ID [general|key|major]）")
    parser.add_argument("--transition", nargs=3, metavar=("ID", "FROM", "TO"),
                        help="流转 proposal（阶段可不填FROM，填auto）")
    parser.add_argument("--optimize", metavar="ID", help="执行一轮对抗优化")
    parser.add_argument("--auto-optimize", metavar="ID", help="自动优化直到达标")
    parser.add_argument("--feedback", nargs=2, metavar=("ID", "FILE"),
                        help="提交人工反馈（--feedback ID 意见文件路径）")
    parser.add_argument("--verdict", default="major_revision",
                        help="审核结论（approve/minor_revision/major_revision/reject/redirect）")
    parser.add_argument("--cron-sweep", action="store_true",
                        help="执行 cron 扫描（扫描 optimizing 区，各执行一轮优化）")
    parser.add_argument("--health-check", action="store_true",
                        help="执行健康检查（检测异常和空转）")
    parser.add_argument("--daily-orchestrate", action="store_true",
                        help="每日编排（健康检查+优化扫描+结果确认，容错）")
    parser.add_argument("--setup-cron", nargs="?", const="0 9 * * *", metavar="SCHEDULE",
                        help="配置每日编排 cron（默认 0 9 * * *）")
    # v6.7.6: 负反馈告警清除
    parser.add_argument("--clear-negative-feedback", metavar="ID",
                        help="清除指定 proposal 的负反馈告警（需人工确认后使用）")
    # v6.7.5: 小型化 cron 框架 CLI
    parser.add_argument("--worker-step", metavar="ID",
                        help="worker 入口：执行指定 proposal 的下一个 pending checkpoint job")
    parser.add_argument("--orchestrate", action="store_true",
                        help="手动触发每日编排（v2：生成 checkpoint + 确保 worker cron）")
    parser.add_argument("--repair", action="store_true",
                        help="手动触发修复扫描（处理 stuck/failed checkpoint 与缺失 worker）")
    parser.add_argument("--dry-run", action="store_true",
                        help="与 --repair 联用：只预览不修改")
    parser.add_argument("--setup-cron-v2", action="store_true",
                        help="安装 v2 cron 框架（orchestrate + repair + per-proposal workers + weekend）")
    parser.add_argument("--worker-schedule", default="", metavar="CRON",
                        help="强制统一 worker cron 调度表达式（默认留空，自动按 6 分钟间隔错开，周中运行）")
    parser.add_argument("--teardown-cron-v2", action="store_true",
                        help="卸载所有 v2 lifecycle cron")
    parser.add_argument("--setup-weekend", action="store_true",
                        help="安装周末任务 cron（输入/输出/反思）")
    parser.add_argument("--teardown-weekend", action="store_true",
                        help="卸载周末任务 cron")
    # v6.7.12: 全局微调度器（5 分钟一轮， researcher 4 子任务连贯执行）
    parser.add_argument("--micro-scheduler", action="store_true",
                        help="手动运行一次全局微调度器")
    parser.add_argument("--setup-micro-scheduler", action="store_true",
                        help="安装全局微调度器 cron（每 5 分钟）")
    parser.add_argument("--remove-micro-scheduler", action="store_true",
                        help="卸载全局微调度器 cron")
    # v6.8.1: 看板与故障恢复
    parser.add_argument("--kanban", action="store_true",
                        help="显示系统看板状态")
    parser.add_argument("--reset-stuck", metavar="ID",
                        help="强制重置指定 proposal 的 failed job（--reset-stuck ID）")
    # v6.8.1: 任务系统集成
    parser.add_argument("--sync-lifecycle-tasks", action="store_true",
                        help="同步当前生命周期状态到任务系统")
    parser.add_argument("--sync-lifecycle-history", action="store_true",
                        help="同步历史优化轮次到任务系统")
    args = parser.parse_args(argv)

    lc = ProposalLifecycle()

    # v6.7.5: 新 cron 框架命令使用 LifecycleCronController
    if any([args.worker_step, args.orchestrate, args.repair, args.setup_cron_v2, args.teardown_cron_v2,
            args.setup_weekend, args.teardown_weekend,
            args.micro_scheduler, args.setup_micro_scheduler, args.remove_micro_scheduler,
            args.kanban, args.reset_stuck,
            args.sync_lifecycle_tasks, args.sync_lifecycle_history]):
        # 延迟导入避免循环依赖
        from lifecycle_cron_framework import LifecycleCronController
        ctrl = LifecycleCronController()

        if args.worker_step:
            result = ctrl.execute_next_job(args.worker_step)
            print(f"worker {args.worker_step}: executed={result.get('executed')} "
                  f"success={result.get('success')} job={result.get('job_id', '-')}")
            if result.get('error'):
                print(f"  error: {result['error']}")
            return 0 if result.get('success') else 1

        if args.orchestrate:
            result = ctrl.run_orchestrator()
            print(f"=== 每日编排完成 (v2) ===")
            print(f"optimizing: {result.get('optimizing_count')} "
                  f"workers_created: {result.get('workers_created')} "
                  f"checkpoints_added: {result.get('checkpoints_added')}")
            print(f"health_after: {'🟢' if result['health_after']['healthy'] else '🔴'} "
                  f"({result['health_after']['alerts']} alerts)")
            return 0

        if args.repair:
            result = ctrl.run_repair(dry_run=args.dry_run)
            print(f"=== 修复扫描完成 (dry_run={result.get('dry_run')}) ===")
            for item in result.get("repaired", []):
                actions = item.get("actions", [])
                label = item.get("proposal_id") or item.get("job", "?")
                print(f"  {label}: {actions if actions else 'ok'}")
            pipeline_repaired = result.get("pipeline_repaired", [])
            if pipeline_repaired:
                for item in pipeline_repaired:
                    actions = item.get("actions", [])
                    label = item.get("proposal_id") or item.get("job", "?")
                    print(f"  [pipeline] {label}: {actions if actions else 'ok'}")
            return 0

        if args.setup_cron_v2:
            result = ctrl.setup_cron_framework(worker_interval=args.worker_schedule)
            print("=== v2 cron 框架安装结果 ===")
            print(f"worker schedule: {args.worker_schedule or '自动错开，周中运行（Mon-Fri）'}")
            print(f"removed_old: {result.get('removed_old', [])}")
            print(f"orchestrate: {result.get('orchestrate', {}).get('message')}")
            print(f"repair: {result.get('repair', {}).get('message')}")
            print(f"first_orchestrate: optimizing={result.get('first_orchestrate', {}).get('optimizing_count')}")
            weekend = result.get("weekend", {})
            if weekend:
                print("weekend crons:")
                for c in weekend.get("created", []):
                    cron_res = c.get("result", {})
                    print(f"  {c['cron']}: {cron_res.get('message', cron_res.get('error', '?'))}")
            return 0 if result.get("success") else 1

        if args.teardown_cron_v2:
            result = ctrl.teardown_cron_framework()
            print(f"=== 已卸载 v2 cron: {result.get('removed', [])} ===")
            return 0

        if args.setup_weekend:
            result = ctrl.setup_weekend_crontab()
            print("=== 周末任务 cron 安装结果 ===")
            for c in result.get("created", []):
                cron_res = c.get("result", {})
                print(f"  {c['cron']}: {cron_res.get('message', cron_res.get('error', '?'))}")
            return 0 if result.get("success") else 1

        if args.teardown_weekend:
            result = ctrl.teardown_weekend_crontab()
            print(f"=== 已卸载周末 cron: {result.get('removed', [])} ===")
            return 0

        if args.micro_scheduler:
            result = ctrl.run_micro_scheduler()
            print("=== 全局微调度器执行完成 ===")
            print(f"executed_count: {result.get('executed_count', 0)}")
            for item in result.get('executed', []):
                print(f"  {item.get('proposal_id')} {item.get('job_id')} "
                      f"step={item.get('step')} success={item.get('success')}")
                if item.get('error'):
                    print(f"    error: {item['error']}")
            return 0 if result.get('success') else 1

        if args.setup_micro_scheduler:
            result = ctrl.schedule_micro_scheduler()
            print(f"=== 全局微调度器 cron 安装结果 ===")
            print(f"message: {result.get('message')}")
            print(f"cron_id: {result.get('cron_job_id')}")
            return 0 if result.get('success') else 1

        if args.remove_micro_scheduler:
            result = ctrl.remove_micro_scheduler()
            print(f"=== 已卸载微调度器 cron: {result.get('removed', [])} ===")
            return 0

        if args.sync_lifecycle_tasks:
            result = ctrl.sync_lifecycle_to_task_manager()
            print(f"=== 生命周期任务同步完成 ===")
            print(f"同步数量: {result.get('synced', 0)}")
            for detail in result.get("details", []):
                print(f"  {detail.get('action', '?')}: {detail.get('proposal_id')} "
                      f"r{detail.get('round')} → {detail.get('task_id')} "
                      f"进度 {detail.get('progress', 0)}%")
            if result.get("error"):
                print(f"错误: {result['error']}")
            # 更新看板中的 task_sync 字段
            _update_kanban_task_sync(ctrl)
            return 0

        if args.sync_lifecycle_history:
            result = ctrl.sync_lifecycle_history_tasks()
            print(f"=== 历史轮次同步完成 ===")
            print(f"同步数量: {result.get('synced', 0)}")
            for detail in result.get("details", []):
                print(f"  {detail.get('proposal_id')} r{detail.get('round')} "
                      f"→ {detail.get('task_id')}")
            if result.get("error"):
                print(f"错误: {result['error']}")
            # 更新看板中的 task_sync 字段
            _update_kanban_task_sync(ctrl)
            return 0

        if args.kanban:
            from common import load_json
            from paths import PROJECT_ROOT
            kanban_path = PROJECT_ROOT / "memory" / "system-kanban.json"
            if not kanban_path.exists():
                print("看板文件不存在，请先运行微调度器")
                return 1
            kanban = load_json(kanban_path, default={})
            print("=== 系统看板 ===")
            print(f"更新时间: {kanban.get('updated_at_local', '?')}")
            print(f"日期: {kanban.get('day_key', '?')}")
            current = kanban.get("current", {})
            print(f"时段: {current.get('slot', '不在时段内')}")
            print(f"聚焦课题: {current.get('focus_proposal', '无')}")
            print(f"优化中课题数: {current.get('proposals_in_optimizing', 0)}")
            print()
            proposals = kanban.get("proposals", [])
            if proposals:
                print(f"课题状态 ({len(proposals)} 个):")
                print(f"{'课题ID':36s} {'轮次':4s} {'分数':5s} {'Job进度':10s} {'失败':4s} {'卡住':4s} {'下一Job':20s}")
                print("-" * 90)
                for p in proposals:
                    stuck = "⚠" if p.get("stuck") else "✓"
                    print(f"{p['proposal_id']:36s} {p['round']:4d} {p['score']:5.2f} {p['jobs']:10s} {p['failed']:4d} {stuck:4s} {p.get('next_job', '-') or '-':20s}")
            history = kanban.get("execution_history", [])
            print(f"\n最近执行 ({len(history)} 条):")
            print(f"{'时间':22s} {'课题':36s} {'步骤':20s} {'结果':6s} {'错误'}")
            print("-" * 100)
            for h in history[-10:]:
                at = h.get("at", "?")[11:19] if len(h.get("at", "")) >= 19 else h.get("at", "?")
                pid = (h.get("proposal_id") or "?")[:36]
                step = (h.get("step") or "?")[:20]
                ok = "✓" if h.get("success") else "✗"
                err = (h.get("error") or "")[:30]
                print(f"{at:22s} {pid:36s} {step:20s} {ok:6s} {err}")
            return 0

        if args.reset_stuck:
            pid = args.reset_stuck
            retried = ctrl._auto_retry_failed_jobs(pid)
            if retried > 0:
                print(f"已重置 {pid} 的 {retried} 个 failed job 为 pending")
            else:
                # 强制重置所有 failed job（即使达到最大重试次数）
                jobs = ctrl._get_jobs(pid)
                forced = 0
                for j in jobs:
                    if j.get("status") == "failed":
                        j["status"] = "pending"
                        j["last_error"] = ""
                        j["attempts"] = 0
                        forced += 1
                if forced:
                    ctrl._save_jobs(pid, jobs)
                    print(f"强制重置 {pid} 的 {forced} 个 failed job 为 pending（重置重试计数）")
                else:
                    print(f"{pid} 无 failed job 需要重置")
            return 0

    # 原有命令继续走 ProposalLifecycle

    if args.dashboard:
        dashboard = lc.get_dashboard()
        print("=== 提案生命周期仪表盘 ===")
        print(f"总数: {dashboard['total']}")
        print("\n按状态:")
        for stage in LIFECYCLE_STAGES:
            count = dashboard["by_status"].get(stage, 0)
            label = {"drafts": "初稿", "optimizing": "优化中",
                     "pending_review": "待校验", "archived": "归档"}[stage]
            print(f"  {label}({stage}): {count}")
        print("\n按类型:")
        for ptype in PROJECT_TYPES:
            count = dashboard["by_type"].get(ptype, 0)
            print(f"  {ptype}: {count}")
        if dashboard["total"] > 0:
            print("\n提案列表:")
            for pid, data in dashboard["proposals"].items():
                print(f"  [{data['status']:14s}] {pid:30s} "
                      f"type={data.get('project_type', '?'):8s} "
                      f"rounds={data.get('optimization_rounds', 0):2d} "
                      f"score={data.get('last_score', 0):.2f}")
        return 0

    if args.list:
        proposals = lc.list_by_status(args.list)
        print(f"=== {args.list} 区（{len(proposals)} 个）===")
        for p in proposals:
            print(f"  {p['proposal_id']:30s} type={p['project_type']:8s} "
                  f"rounds={p['optimization_rounds']:2d} score={p['last_score']:.2f}")
        return 0

    if args.register:
        pid = args.register[0]
        ptype = args.register[1] if len(args.register) > 1 else "general"
        result = lc.register(pid, project_type=ptype)
        print(f"注册: {result}")
        return 0 if result.get("success") else 1

    if args.transition:
        pid, _from, to = args.transition
        result = lc.transition(pid, to)
        print(f"流转: {result}")
        return 0 if result.get("success") else 1

    if args.optimize:
        result = lc.optimize_cycle(args.optimize)
        print(f"优化轮 {result.get('round', '?')}: "
              f"score {result.get('score_before', 0):.2f} → {result.get('score_after', 0):.2f} "
              f"(Δ{result.get('score_delta', 0):+.4f})")
        print(f"问题: {result.get('issues_found', 0)}个 "
              f"(high: {result.get('high_issues', 0)})")
        print(f"完成: {'是' if result.get('done') else '否'} - {result.get('reason', '')}")
        return 0 if result.get("success") else 1

    if args.auto_optimize:
        result = lc.auto_optimize_and_advance(args.auto_optimize)
        print(f"自动优化完成: {result.get('rounds', 0)} 轮, "
              f"最终分数 {result.get('final_score', 0):.2f}")
        print(f"移入待校验: {'是' if result.get('advanced') else '否'} - {result.get('reason', '')}")
        return 0 if result.get("success") else 1

    if args.feedback:
        pid, filepath = args.feedback
        feedback_text = Path(filepath).read_text(encoding="utf-8")
        result = lc.submit_feedback(pid, feedback_text, verdict=args.verdict)
        print(f"反馈处理: verdict={result.get('verdict')}")
        print(f"归档: {'是' if result.get('archived') else '否'}")
        if result.get("structured_feedback"):
            sf = result["structured_feedback"]
            if sf.get("structured"):
                issues = sf["structured"].get("issues", [])
                print(f"结构化: {len(issues)} 个 issue")
        return 0 if result.get("success") else 1

    if args.cron_sweep:
        result = lc.run_cron_sweep()
        print(f"=== cron 扫描完成: {result.get('swept', 0)} 个 proposal ===")
        if result.get("empty"):
            print("  optimizing 区为空")
        for r in result.get("results", []):
            pid = r["proposal_id"]
            if "error" in r:
                print(f"  ✗ {pid}: {r['error']}")
            else:
                res = r["result"]
                print(f"  {'✓' if res.get('done') else '◐'} {pid}: "
                      f"轮{res.get('round', '?')} score={res.get('score_after', 0):.2f} "
                      f"{'→ 待校验' if res.get('done') else '继续优化'}")
        return 0

    if args.health_check:
        result = lc.run_health_check()
        status_icon = "🟢" if result["healthy"] else "🔴"
        print(f"{status_icon} 健康检查: {'健康' if result['healthy'] else '有告警'}")
        print(f"告警数: {len(result['alerts'])}")
        for alert in result["alerts"]:
            level_icon = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(alert["level"], "⚪")
            print(f"  {level_icon} [{alert['type']}] {alert['message']}")
            if "proposals" in alert:
                for p in alert["proposals"]:
                    if isinstance(p, dict):
                        print(f"      - {p.get('id', '?')} score={p.get('score', 0):.2f}")
                    else:
                        print(f"      - {p}")
        print(f"\n状态统计:")
        for stage, count in result["stats"]["by_status"].items():
            print(f"  {stage}: {count}")
        return 0 if result["healthy"] else 1

    if args.daily_orchestrate:
        result = lc.run_daily_orchestrator()
        print("=== 每日编排完成 ===")
        sweep = result.get("sweep", {})
        print(f"优化扫描: {sweep.get('swept', 0)}个 "
              f"(成功{sweep.get('success', 0)} 失败{sweep.get('failed', 0)} "
              f"达标{sweep.get('advanced', 0)})")
        if sweep.get("empty"):
            print("  optimizing 区为空")
        health = result.get("health_after", {})
        status = "🟢" if health.get("healthy") else "🔴"
        print(f"{status} 最终健康: {'健康' if health.get('healthy') else '有告警'} "
              f"({health.get('alert_count', 0)}个告警)")
        for alert in health.get("alerts", []):
            level_icon = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(alert["level"], "⚪")
            print(f"  {level_icon} {alert['message']}")
        return 0

    if args.setup_cron is not None:
        result = lc.setup_optimization_cron(schedule=args.setup_cron)
        print(result.get("message", ""))
        return 0 if result.get("success") else 1

    if args.clear_negative_feedback:
        result = lc.clear_negative_feedback(args.clear_negative_feedback, reason="人工确认后清除")
        if result.get("success"):
            print(f"✓ 已清除 {args.clear_negative_feedback} 的负反馈告警")
            if result.get("cleared_at"):
                print(f"  清除时间: {result['cleared_at']}")
        else:
            print(f"✗ 清除失败: {result.get('error', '')}")
        return 0 if result.get("success") else 1

    parser.print_help()
    return 0
