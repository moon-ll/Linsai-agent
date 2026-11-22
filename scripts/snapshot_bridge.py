#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""snapshot 桥接恢复点保鲜（v8.0.44，48h 推进期专项工具）。

背景：main 未推送范围含 v7.0.2 裁决前入库的 4.2GB 遗留 PDF，
GitHub 端 main 更新被拒/挂死（见 memory/self-optimize/worklist.json
"main 历史推送解阻断方案裁决"）。main 历史同步期间，异地恢复点由
orphan 快照分支承担：本脚本对比 HEAD 树与远程快照分支树，有差异才
commit-tree 生成新 orphan 快照并推送（纯 plumbing，不触碰工作树、
不改任何历史、只增改 snapshot 远程分支）。

分支策略：
- refs/heads/snapshot-latest  悬浮恢复点（--force 覆盖，单写者工具）
- refs/heads/snapshot-YYYYMMDD 每日锚点（仅当天首个差异时创建，不覆盖）

用法示例：
    python3 scripts/snapshot_bridge.py             # 对比+按需推送
    python3 scripts/snapshot_bridge.py --dry-run   # 只对比不推送
    python3 scripts/snapshot_bridge.py --self-check
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

PROJECT_ROOT = Path(__file__).parent.parent
FLOATING_REF = "refs/heads/snapshot-latest"
REMOTE = "origin"


def _run_git(args: list, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(["git"] + args, capture_output=True, text=True, timeout=timeout, cwd=str(PROJECT_ROOT))


def head_tree() -> str:
    """HEAD 树 SHA（不存在则抛错）。"""
    r = _run_git(["rev-parse", "HEAD^{tree}"])
    if r.returncode != 0:
        raise RuntimeError(f"HEAD 树解析失败: {r.stderr.strip()}")
    return r.stdout.strip()


def head_sha() -> str:
    r = _run_git(["rev-parse", "HEAD"])
    return r.stdout.strip() if r.returncode == 0 else "?"


def remote_snapshot_commit(ref: str) -> Optional[str]:
    """远程分支当前 commit SHA（分支不存在返回 None）。"""
    r = _run_git(["ls-remote", REMOTE, ref], timeout=60)
    if r.returncode != 0:
        raise RuntimeError(f"ls-remote 失败: {r.stderr.strip()}")
    line = r.stdout.strip().splitlines()[0] if r.stdout.strip() else ""
    return line.split("\t")[0] if line else None


def commit_tree_sha(commit_sha: str) -> Optional[str]:
    """commit 对象的树 SHA（解析失败返回 None）。"""
    if not commit_sha:
        return None
    r = _run_git(["cat-file", "commit", commit_sha])
    if r.returncode != 0:
        return None
    for line in r.stdout.splitlines():
        if line.startswith("tree "):
            return line.split()[1]
    return None


def should_refresh(head_tree_sha: str, remote_tree_sha: Optional[str]) -> bool:
    """纯决策：远程树缺失或与 HEAD 不同 → 需要刷新（不碰 git，可离线单测）。"""
    if not remote_tree_sha:
        return True
    return remote_tree_sha != head_tree_sha


def resolve_remote_tree(remote_commit: Optional[str]) -> Optional[str]:
    """远程快照 commit → 树 SHA（缺失/解析失败统一返回 None，保守判刷新）。"""
    if not remote_commit:
        return None
    return commit_tree_sha(remote_commit)


def make_snapshot_commit(tree_sha: str, base_sha: str) -> str:
    """orphan 快照提交（commit-tree，无父）。"""
    msg = (
        f"snapshot {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}: 工作台当前状态快照（orphan 无历史）\n\n"
        f"base(main HEAD): {base_sha}\n"
        f"背景：main 历史含 4.2GB 遗留 PDF 推送被拒，main 同步裁决前由本分支承担恢复点\n"
    )
    r = _run_git(["commit-tree", tree_sha, "-m", msg])
    if r.returncode != 0:
        raise RuntimeError(f"commit-tree 失败: {r.stderr.strip()}")
    return r.stdout.strip()


def push_ref(commit_sha: str, ref: str, lease: Optional[str] = None, timeout: int = 900) -> bool:
    """推送（floating 用 --force 覆盖；锚点仅在缺失时创建）。

    注：本机 CommandLineTools git 对 --force-with-lease=<ref>=<expect> 显式
    期望值语法仍按非快进拒绝（2026-11-21 实测），floating 分支仅本工具
    单写者，竞态可忽略，故降级纯 --force。
    """
    args = ["push", REMOTE, f"{commit_sha}:{ref}"]
    if lease:
        args.insert(2, "--force")
    r = _run_git(args, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"push {ref} 失败: {r.stderr.strip()[-300:]}")
    return True


def refresh(dry_run: bool = False) -> Dict[str, Any]:
    """主流程：对比 → 按需提交并刷新 floating + 每日锚点。"""
    tree = head_tree()
    base = head_sha()
    result: Dict[str, Any] = {"head_tree": tree, "base": base, "actions": []}
    remote_commit = remote_snapshot_commit(FLOATING_REF)
    result["remote_snapshot_commit"] = remote_commit
    if not should_refresh(tree, resolve_remote_tree(remote_commit)):
        result["actions"].append("✓ 快照已是最新（树一致），跳过")
        return result
    commit = make_snapshot_commit(tree, base)
    result["snapshot_commit"] = commit
    if dry_run:
        result["actions"].append(f"○ dry-run：将推送 {commit[:10]} → {FLOATING_REF}")
        return result
    push_ref(commit, FLOATING_REF, lease=remote_commit)
    result["actions"].append(f"✓ snapshot-latest → {commit[:10]}")
    today = datetime.now().strftime("%Y%m%d")  # 本地日期（锚点语义与用户日历一致）
    anchor = f"refs/heads/snapshot-{today}"
    if remote_snapshot_commit(anchor) is None:
        push_ref(commit, anchor)
        result["actions"].append(f"✓ 每日锚点 {anchor.split('/')[-1]} → {commit[:10]}")
    return result


def _self_check() -> int:
    ok = True
    # 决策逻辑
    if should_refresh("t1", None) is not True:
        print("✗ 远程缺失应判刷新"); ok = False
    if should_refresh("t1", "?") is not True:
        print("✗ 远程不可解析应判刷新"); ok = False
    # dry-run 全链（真实只读 + commit-tree 落本地对象库，无网络写）
    res = refresh(dry_run=True)
    if not res.get("actions"):
        print("✗ dry-run 无动作输出"); ok = False
    print("✓ snapshot_bridge 自检通过" if ok else "✗ 自检未通过")
    for a in res.get("actions", []):
        print(" ", a)
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="snapshot 桥接恢复点保鲜（零 LLM）")
    ap.add_argument("--dry-run", action="store_true", help="只对比不推送")
    ap.add_argument("--self-check", action="store_true", help="自检")
    args = ap.parse_args()
    if args.self_check:
        return _self_check()
    try:
        res = refresh(dry_run=args.dry_run)
        for a in res["actions"]:
            print(a)
        return 0
    except Exception as e:  # noqa: BLE001
        print(f"✗ snapshot_bridge: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
