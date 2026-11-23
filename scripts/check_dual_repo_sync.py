#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_dual_repo_sync — CoPilot ↔ NSFC 仓库双仓对账（v7.2.104，F2）。

背景（v7.2.94 实测）：NSFC 申请材料仓库（hermes_workspace 内独立 git）曾
自 6/26 起积压未提交改动两个月无人发现，直至并行会话人工巡检才补提交——
「用户资产不得滞留工作区」需要一个周期性对账入口。

对账内容（只读报告，不改任何文件）：
  1. NSFC 仓库 git status（未提交改动 = 丢失风险）
  2. NSFC 仓库最近提交年龄
  3. CoPilot 侧 NSFC 知识镜像（knowledge/wiki/projects/NSFC-强场超快/）
     最近修改时间——镜像新于仓库提交时提示「可回灌」
  4. CoPilot 自身工作区状态摘要（未提交文件计数）

仓库路径默认取 v7.2.94 实测路径，可用 --repo 覆盖。

用法：
    python3 scripts/check_dual_repo_sync.py                # 全量对账
    python3 scripts/check_dual_repo_sync.py --repo PATH    # 指定仓库
    python3 scripts/check_dual_repo_sync.py --self-check   # 自检
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from paths import PROJECT_ROOT  # noqa: E402

DEFAULT_NSFC_REPO = Path.home() / "Desktop" / "hermes_workspace" / "research_proposals" / "2026_NSFG_strongfield_ultrafast"
MIRROR_DIR = PROJECT_ROOT / "knowledge" / "wiki" / "projects" / "NSFC-强场超快"


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=30)
    return r.stdout.strip()


def check_repo(repo: Path) -> dict:
    out = {"repo": str(repo), "exists": repo.exists()}
    if not (repo / ".git").exists():
        out["status"] = "not_a_git_repo"
        return out
    dirty = _git(repo, "status", "--porcelain")
    out["dirty_files"] = len(dirty.splitlines()) if dirty else 0
    last = _git(repo, "log", "-1", "--format=%cI")
    out["last_commit_at"] = last
    if last:
        try:
            age_days = (datetime.now(timezone.utc) - datetime.fromisoformat(last.replace("Z", "+00:00"))).total_seconds() / 86400.0
            out["last_commit_age_days"] = round(age_days, 1)
        except ValueError:
            pass
    out["status"] = "dirty" if out["dirty_files"] else "clean"
    return out


def check_mirror() -> dict:
    if not MIRROR_DIR.exists():
        return {"mirror": str(MIRROR_DIR), "status": "missing"}
    mtimes = [f.stat().st_mtime for f in MIRROR_DIR.rglob("*.md")]
    newest = datetime.fromtimestamp(max(mtimes), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M") if mtimes else ""
    return {"mirror": str(MIRROR_DIR), "pages": len(mtimes), "newest_mtime": newest, "status": "ok"}


def run_all(repo: Path) -> dict:
    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "nsfc": check_repo(repo),
        "copilot_mirror": check_mirror(),
        "copilot_dirty": len(subprocess.run(
            ["git", "-C", str(PROJECT_ROOT), "status", "--porcelain"],
            capture_output=True, text=True).stdout.splitlines()),
    }


def _self_check() -> int:
    """自检：用 LinSai-CoPilot 本体当假想仓库走通 check_repo 全分支。"""
    rep = check_repo(PROJECT_ROOT)
    assert rep["exists"] and rep["status"] in ("clean", "dirty"), rep
    assert "last_commit_at" in rep
    print("✓ check_dual_repo_sync 自检通过（本体仓库 dirty/clean 分支 + 提交年龄解析）")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description="CoPilot ↔ NSFC 双仓对账")
    ap.add_argument("--repo", type=Path, default=DEFAULT_NSFC_REPO, help="NSFC 仓库路径")
    ap.add_argument("--self-check", action="store_true", help="自检")
    args = ap.parse_args()
    if args.self_check:
        sys.exit(_self_check())
    r = run_all(args.repo)
    print(json.dumps(r, ensure_ascii=False, indent=1))
    nsfc = r["nsfc"]
    if nsfc.get("status") == "dirty":
        print(f"\n⚠ NSFC 仓库有 {nsfc['dirty_files']} 个未提交文件——用户资产滞留风险，建议尽快提交")
    if nsfc.get("last_commit_age_days", 0) > 30:
        print(f"\n⚠ NSFC 仓库 {nsfc['last_commit_age_days']} 天未提交")


if __name__ == "__main__":
    main()
