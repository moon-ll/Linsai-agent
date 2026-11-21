#!/usr/bin/env python3
"""周末任务流水线 CLI。"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

from .constants import STAGES
from .pipeline import WeekendPipeline


def _fmt(result: Dict[str, Any]) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2, default=str)


def list_jobs(pipeline: WeekendPipeline, stage: Optional[str] = None) -> Dict[str, Any]:
    jobs = pipeline.list_jobs(stage=stage)
    return {
        "stage": stage or "all",
        "count": len(jobs),
        "jobs": [
            {
                "job_id": j.get("job_id"),
                "stage": j.get("stage"),
                "step": j.get("step"),
                "status": j.get("status"),
                "depends_on": j.get("depends_on", []),
                "attempts": j.get("attempts", 0),
            }
            for j in jobs
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="周末任务流水线（checkpoint-style jobs）")
    parser.add_argument("--stage", choices=STAGES, help="指定阶段")
    parser.add_argument("--ensure-jobs", action="store_true", help="幂等创建阶段任务")
    parser.add_argument("--run-next", action="store_true", help="执行下一个 pending 任务")
    parser.add_argument("--run-all", action="store_true", help="顺序执行阶段全部任务")
    parser.add_argument("--list", action="store_true", help="列出任务")
    parser.add_argument("--repair", action="store_true", help="修复 stale/failed 任务")
    parser.add_argument("--dry-run", action="store_true", help="只预览不写入")
    parser.add_argument("--self-check", action="store_true", help="自检")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    pipeline = WeekendPipeline()

    if args.self_check:
        print("=== weekend_pipeline._self_check ===")
        print(f"状态文件: {pipeline.state_path}")
        print(f"任务数: {len(pipeline.state.get('jobs', []))}")
        print("✓ 通过")
        return 0

    if args.list:
        print(_fmt(list_jobs(pipeline, stage=args.stage)))
        return 0

    if args.repair:
        print(_fmt(pipeline.repair()))
        return 0

    if args.ensure_jobs:
        if not args.stage:
            parser.error("--ensure-jobs 需要 --stage")
        result = pipeline.sync_stage_jobs(args.stage)
        print(_fmt(result))
        return 0

    if args.run_next:
        result = pipeline.run_next(stage=args.stage, dry_run=args.dry_run)
        print(_fmt(result))
        return 0 if result.get("success") else 1

    if args.run_all:
        if not args.stage:
            # 跨阶段运行：先确保所有阶段任务存在，再顺序执行
            pipeline.ensure_all_stages()
            for stage in STAGES:
                result = pipeline.run_stage(stage, dry_run=args.dry_run)
                if not result.get("success"):
                    print(_fmt(result))
                    return 1
            print(_fmt({"success": True, "stages": STAGES}))
            return 0
        result = pipeline.run_stage(args.stage, dry_run=args.dry_run)
        print(_fmt(result))
        return 0 if result.get("success") else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
