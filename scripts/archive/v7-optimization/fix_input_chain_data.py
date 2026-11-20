#!/usr/bin/env python3
"""修复 08-16 输入链路数据污染（v6.9.18 一次性数据修复）。

背景：08-16 凌晨周末输入链全链首跑，知识簇路由泛滥（141 簇 → 72 new）
注册了 54 个弱簇课题进 drafts（46 个 new-idea-NN 占位名），KB 镜像
同步产生 100+ 垃圾页，簇注册表被乱聚簇污染。本脚本在链路重构
（v6.9.18）落地后清理存量污染：

1. 删 08-16 批次 auto_idea 注册的垃圾 drafts 课题（目录归档到
   backups/input-chain-fix-{date}/，不直接删）+ 清 _lifecycle.json 状态；
2. 清 KB 垃圾镜像（reports/versions 下的镜像页移入备份）+ 重建
   proposals-index/MOC（调用 proposal_kb_sync）；
3. 重置簇注册表：clusters.json 归档；新注册表 = 旧 orphans + 旧簇
   member_summaries 退回 orphan 池（保留已花的 LLM 摘要成本）。
   processed_sources 原样保留（防重复摘要）。

用法：
    python3 scripts/fix_input_chain_data.py            # dry-run 预览
    python3 scripts/fix_input_chain_data.py --apply    # 执行
    python3 scripts/fix_input_chain_data.py --self-check
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import file_lock, load_json, now_utc, save_json
from paths import PROJECT_ROOT

try:
    from logger import get_logger
    _log = get_logger("fix_input_chain")
except Exception:
    _log = None

LIFECYCLE_PATH = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"
DRAFTS_DIR = PROJECT_ROOT / "research_proposals" / "drafts"
CLUSTERS_PATH = PROJECT_ROOT / "memory" / "weekend-input" / "clusters.json"
NSFC_KB_DIR = PROJECT_ROOT / "knowledge" / "wiki" / "projects" / "NSFC-强场超快"

# 本次清理针对的注册批次（auto_idea 来源 + 20260816 批次日期）
JUNK_BATCH_DATE = "20260816"


def find_junk_drafts(lifecycle: Dict[str, Any]) -> List[str]:
    """识别 08-16 批次 auto_idea 注册的垃圾 drafts 课题。

    判据：proposal_id 以 -{JUNK_BATCH_DATE} 结尾，或 state 的
    source=auto_idea 且 created_at 落在 2026-08-15/16。
    """
    junk: List[str] = []
    for pid, st in (lifecycle.get("proposals") or {}).items():
        if pid.endswith(f"-{JUNK_BATCH_DATE}") or (
            st.get("source") == "auto_idea"
            and str(st.get("created_at", ""))[:10] in ("2026-08-15", "2026-08-16")
        ):
            junk.append(pid)
    # drafts 目录里 _lifecycle 没有状态的孤儿目录（同批次命名）一并处理
    if DRAFTS_DIR.exists():
        for d in DRAFTS_DIR.iterdir():
            if d.is_dir() and d.name.endswith(f"-{JUNK_BATCH_DATE}") and d.name not in junk:
                junk.append(d.name)
    return sorted(set(junk))


def fix_proposals(dry_run: bool = True, junk: Optional[List[str]] = None) -> Dict[str, Any]:
    """动作 1：归档垃圾 drafts 课题 + 清生命周期状态。

    junk 传入时跳过识别（run 统一识别，apply 后无法重算）。
    """
    lifecycle = load_json(LIFECYCLE_PATH, default={})
    if "proposals" not in lifecycle:
        lifecycle["proposals"] = {}
    if junk is None:
        junk = find_junk_drafts(lifecycle)
    backup_dir = PROJECT_ROOT / "backups" / f"input-chain-fix-{now_utc()[:10].replace('-', '')}"
    moved, cleaned = 0, 0

    for pid in junk:
        src = DRAFTS_DIR / pid
        if src.exists():
            dst = backup_dir / "drafts" / pid
            if not dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
            moved += 1
        if pid in (lifecycle.get("proposals") or {}):
            if not dry_run:
                del lifecycle["proposals"][pid]
            cleaned += 1

    if not dry_run and cleaned:
        lifecycle["updated_at"] = now_utc()
        with file_lock("lifecycle-state"):
            save_json(LIFECYCLE_PATH, lifecycle)

    return {"junk_found": len(junk), "dirs_moved": moved, "states_cleaned": cleaned,
            "backup_dir": str(backup_dir.relative_to(PROJECT_ROOT)) if moved else ""}


def fix_kb_mirrors(junk: List[str], dry_run: bool = True) -> Dict[str, Any]:
    """动作 2：清 KB 垃圾镜像页（reports/versions），索引由 sync_all 重建。"""
    backup_dir = PROJECT_ROOT / "backups" / f"input-chain-fix-{now_utc()[:10].replace('-', '')}"
    moved = 0
    for sub in ("reports", "versions"):
        d = NSFC_KB_DIR / sub
        if not d.exists():
            continue
        for pid in junk:
            f = d / f"{pid}.md"
            if f.exists():
                if not dry_run:
                    dst = backup_dir / "kb" / sub / f.name
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(f), str(dst))
                moved += 1
    return {"kb_mirrors_moved": moved}


def rebuild_kb_index(dry_run: bool = True) -> Dict[str, Any]:
    """动作 2b：重建 proposals-index / MOC（垃圾课题移除后索引失真）。"""
    if dry_run:
        return {"index_rebuilt": False, "message": "dry-run 跳过索引重建"}
    try:
        from proposal_kb_sync import ProposalKbSync
        syncer = ProposalKbSync()
        result = syncer.sync_all(dry_run=False)
        return {"index_rebuilt": bool(result.get("success", True)),
                "synced": result.get("synced", result)}
    except Exception as e:
        if _log:
            _log.warning(f"KB 索引重建失败: {e}")
        return {"index_rebuilt": False, "error": str(e)}


def fix_cluster_registry(dry_run: bool = True) -> Dict[str, Any]:
    """动作 3：簇注册表重置（归档 + 未路由簇成员退回 orphan 池）。

    linked 簇（已路由注入课题）整体保留——既避免成员重新聚簇造成
    下周重复注入，也维持 form_new_clusters 对已消费主题的查重屏障。
    open/closed 簇的成员摘要退回 orphan 池（保留已花的 LLM 成本，
    交给修复后的 2-gram 聚类重新归簇）。processed_sources 不动。
    """
    if not CLUSTERS_PATH.exists():
        return {"archived": False, "message": "clusters.json 不存在，无需重置"}
    data = load_json(CLUSTERS_PATH, default={})
    old_clusters = data.get("clusters", []) or []
    old_orphans = data.get("orphans", []) or []

    kept_linked = [c for c in old_clusters if c.get("status") == "linked"]
    # 成员摘要退回 orphan：以 source_id 去重，orphan 已有的不覆盖
    orphan_index = {o.get("source_id"): o for o in old_orphans if o.get("source_id")}
    demoted = 0
    for c in old_clusters:
        if c.get("status") == "linked":
            continue
        fallback_ts = c.get("created_at", "") or c.get("updated_at", "") or now_utc()
        for ms in c.get("member_summaries", []):
            sid = ms.get("source_id", "")
            if not sid or sid in orphan_index:
                continue
            orphan_index[sid] = {
                "source_id": sid,
                "title": ms.get("title", ""),
                "summary": ms.get("summary", ""),
                "keywords": ms.get("keywords", []) or [],
                "path": ms.get("path", ""),
                "first_seen": fallback_ts,
            }
            demoted += 1

    new_registry = {
        "clusters": kept_linked,
        "orphans": list(orphan_index.values()),
        "reset_at": now_utc(),
        "reset_reason": "v6.9.18 输入链路重构：乱聚 open/closed 簇废弃成员退回 orphan 池，linked 簇保留防重复注入",
        "archived_from": "clusters-archive-" + now_utc()[:10].replace("-", ""),
    }
    if dry_run:
        return {"archived": True, "old_clusters": len(old_clusters),
                "linked_kept": len(kept_linked),
                "old_orphans": len(old_orphans), "demoted_to_orphan": demoted,
                "new_orphans": len(orphan_index), "dry_run": True}

    archive = CLUSTERS_PATH.parent / f"clusters-archive-{now_utc()[:10].replace('-', '')}.json"
    if not archive.exists():
        shutil.copy2(CLUSTERS_PATH, archive)
    save_json(CLUSTERS_PATH, new_registry)
    return {"archived": True, "old_clusters": len(old_clusters),
            "linked_kept": len(kept_linked),
            "old_orphans": len(old_orphans), "demoted_to_orphan": demoted,
            "new_orphans": len(orphan_index), "archive": archive.name}


def fix_ops_entries_in_registry(dry_run: bool = True) -> Dict[str, Any]:
    """动作 4（v6.9.18 补）：清理簇注册表中的运维条目。

    08-16 之前无运维过滤，运维简报（"每日简报空记录/cron 运维"）
    被摘要过并留在 orphan 池/成簇。它们不是学术内容，方向关卡得住
    new 但会永久占据 open 簇。以 sources 的运维判据重扫注册表，
    命中的 orphan 丢弃、成员全是运维条目的簇整簇移除。
    """
    from weekend_pipeline.sources import _is_ops_briefing

    if not CLUSTERS_PATH.exists():
        return {"cleaned": 0}
    data = load_json(CLUSTERS_PATH, default={})
    removed_orphans, removed_clusters = 0, 0

    def _is_ops_entry(entry: Dict[str, Any]) -> bool:
        return _is_ops_briefing(entry.get("title", ""), (entry.get("summary", "") or "") * 3)

    kept_orphans = []
    for o in data.get("orphans", []):
        if _is_ops_entry(o):
            removed_orphans += 1
        else:
            kept_orphans.append(o)
    data["orphans"] = kept_orphans

    # 运维簇无论状态一律移除：open 的会污染路由（08-16 复跑实测被 LLM
    # 判 new 注册运维课题），linked 的也只是被路由进了运维内容
    from weekend_pipeline.input_jobs import _is_ops_cluster
    kept_clusters = []
    for c in data.get("clusters", []):
        if _is_ops_cluster(c):
            removed_clusters += 1
            continue
        kept_clusters.append(c)
    data["clusters"] = kept_clusters

    if not dry_run:
        save_json(CLUSTERS_PATH, data)
    return {"removed_orphans": removed_orphans, "removed_clusters": removed_clusters}


def run(dry_run: bool = True) -> Dict[str, Any]:
    mode = "dry-run 预览" if dry_run else "执行"
    print(f"○ 输入链数据修复（{mode}）")
    # 统一先识别垃圾清单：动作 1/2 共用（apply 模式下动作 1 会清掉
    # _lifecycle.json 中的垃圾状态，事后重算会得到空清单）
    lifecycle = load_json(LIFECYCLE_PATH, default={})
    if "proposals" not in lifecycle:
        lifecycle["proposals"] = {}
    junk = find_junk_drafts(lifecycle)

    r1 = fix_proposals(dry_run, junk=junk)
    print(f"  {'✓' if not dry_run else '○'} 垃圾课题：识别 {r1['junk_found']}，"
          f"目录归档 {r1['dirs_moved']}，状态清理 {r1['states_cleaned']}")
    if r1.get("backup_dir"):
        print(f"    备份位置：{r1['backup_dir']}")

    r2 = fix_kb_mirrors(junk, dry_run)
    print(f"  {'✓' if not dry_run else '○'} KB 镜像清理：{r2['kb_mirrors_moved']} 页")
    r3 = rebuild_kb_index(dry_run)
    if r3.get("index_rebuilt"):
        print("  ✓ KB 索引已重建（proposals-index / MOC）")
    elif dry_run:
        print("  ○ KB 索引重建：dry-run 跳过")
    else:
        print(f"  ⚠ KB 索引重建失败：{r3.get('error', '未知')}")

    r4 = fix_cluster_registry(dry_run)
    if r4.get("archived"):
        print(f"  {'✓' if not dry_run else '○'} 簇注册表重置：旧簇 {r4['old_clusters']}"
              f"（linked 保留 {r4.get('linked_kept', 0)}）/ 旧 orphan {r4['old_orphans']}"
              f" → 退回 {r4['demoted_to_orphan']} 条，新 orphan 池 {r4['new_orphans']} 条")
    else:
        print(f"  ○ 簇注册表：{r4.get('message', '')}")

    # v6.9.18 补：注册表里的运维条目清理（幂等，重复执行安全）
    r5 = fix_ops_entries_in_registry(dry_run)
    if r5.get("removed_orphans") or r5.get("removed_clusters"):
        print(f"  {'✓' if not dry_run else '○'} 运维条目清理：orphan {r5['removed_orphans']} 条 / 整簇 {r5['removed_clusters']} 个")

    if dry_run:
        print(f"⚠ dry-run 未落盘。确认后执行：python3 scripts/fix_input_chain_data.py --apply")
    else:
        print("✓ 修复完成")
    return {"junk": len(junk), "proposals": r1, "kb": r2, "index": r3, "clusters": r4}


def _self_check() -> int:
    """自检：垃圾识别 + orphan 退回逻辑在临时目录验证。"""
    import tempfile
    import fix_input_chain_data as mod

    failures = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        # 场景：1 个垃圾（auto_idea+20260816）+ 1 个正常课题
        lc = {
            "proposals": {
                "general-new-idea-20260816": {"source": "auto_idea", "created_at": "2026-08-16T01:00:00Z", "status": "drafts"},
                "general-bsv-driven-hhg-quantum-20260726": {"source": "manual", "created_at": "2026-07-26T00:00:00Z", "status": "optimizing"},
            }
        }
        save_json(tmp / "_lifecycle.json", lc)
        (tmp / "drafts" / "general-new-idea-20260816").mkdir(parents=True)
        # patch 路径
        orig_lifecycle, orig_drafts = mod.LIFECYCLE_PATH, mod.DRAFTS_DIR
        mod.LIFECYCLE_PATH, mod.DRAFTS_DIR = tmp / "_lifecycle.json", tmp / "drafts"
        junk = mod.find_junk_drafts(lc)
        if junk != ["general-new-idea-20260816"]:
            failures.append(f"垃圾识别错误: {junk}")
        mod.LIFECYCLE_PATH, mod.DRAFTS_DIR = orig_lifecycle, orig_drafts

        # orphan 退回：簇成员 → orphan，去重
        clusters = {"clusters": [{"member_summaries": [
            {"source_id": "paper:a", "title": "A", "summary": "s", "keywords": [], "path": "p"},
        ]}], "orphans": [
            {"source_id": "paper:b", "title": "B", "summary": "s", "keywords": [], "first_seen": "2026-08-01T00:00:00Z"},
        ]}
        save_json(tmp / "clusters.json", clusters)
        orig_clusters = mod.CLUSTERS_PATH
        mod.CLUSTERS_PATH = tmp / "clusters.json"
        r = mod.fix_cluster_registry(dry_run=True)
        if r.get("demoted_to_orphan") != 1 or r.get("new_orphans") != 2:
            failures.append(f"orphan 退回错误: {r}")
        mod.CLUSTERS_PATH = orig_clusters

    if failures:
        for f in failures:
            print(f"✗ {f}")
        return 1
    print("✓ fix_input_chain_data 自检通过（2/2）")
    return 0


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="修复 08-16 输入链路数据污染")
    parser.add_argument("--apply", action="store_true", help="执行修复（默认 dry-run 预览）")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args(argv)
    if args.self_check:
        return _self_check()
    run(dry_run=not args.apply)
    return 0


if __name__ == "__main__":
    sys.exit(main())
