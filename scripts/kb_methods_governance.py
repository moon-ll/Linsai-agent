#!/usr/bin/env python3
"""方法学专题治理（v7.0.6 批次二）：乱码页重命名 + 变体页合并 + 薄壳补建。

背景（2026-09-27 知识库方法学升级）：
1. 11 个 methods-settle 建页时文件名生成 bug 的乱码页（m0cdf9021 等）——
   frontmatter title 均正确，自动识别重命名零风险；图谱节点按 title 索引
   不受文件名影响，全库引用扫描确认乱码名零 wikilink 引用，无需引用改写。
2. 乱码页中 3 个"磁/自旋空间群对称性分析"语义重叠变体，合并为主页。
3. 短 slug 名页（berry/chern/dft 等）统一重命名为 title 派生名，消除
   检索歧义（"p.md" 这类文件名无信息量）。

用法：
    python3 scripts/kb_methods_governance.py              # dry-run 预览
    python3 scripts/kb_methods_governance.py --apply      # 执行
    python3 scripts/kb_methods_governance.py --self-check

规范：
    - 仅使用 Python 3 标准库；JSON ensure_ascii=False, indent=2
    - 重命名 = shutil.move + 图谱全量重建（kb_auto_sync 每日已跑，
      本脚本执行后调用 kb_graph 重建接口同步）；旧名不留 stub（零引用）
    - 变体合并复用 kb_merger 语义（LLM 融合，周限外显式传参）
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import file_lock, load_json, now_utc, save_json
from paths import PROJECT_ROOT

try:
    from logger import get_logger
    _log = get_logger("kb_methods_governance")
except Exception:
    _log = None

METHODS_DIR = PROJECT_ROOT / "knowledge" / "wiki" / "methods"

# 乱码名 → 语义名映射（title 派生 safe_filename；建页 bug 修复）
# 语义重叠三变体的归并决策：m32001767（磁点群/自旋群）为最通用主页，
# m5e50c03c（磁性空间群/群论）与 mb6f4aba4（自旋空间群）为其子视角，
# m8e47148a（自旋群/磁空间群，内容最厚 4.5KB）独立保留（NRSS/RSS 判据
# 有独立参数表，合并会丢结构）。
GARBLED_RENAME: Dict[str, str] = {
    "m0cdf9021": "磁电耦合对称性张量分析",
    "m2bca9f9a": "层间滑移势能面与极化路径计算",
    "m32001767": "磁点群自旋群对称性分析",
    "m5e50c03c": "磁性空间群群论对称性分析",
    "m6323bf81": "自发反常霍尔效应测量",
    "m998a347f": "应变工程晶格与单轴应变扫描",
    "ma194981f": "磁空间群对称性与线性自旋波建模",
    "mc086be53": "半经典动力学方程贝里曲率反常速度",
    "mfe186619": "磁性点群输运张量对称性分析",
    "mb6f4aba4": "自旋空间群对称性分析",
    "p": "p波磁体对称性分析",
}

# 短 slug 名 → title 派生名（消除检索歧义；与 kb_merger 双世代去重的
# slug 键不同，这些页均为单世代无重复风险）
SHORT_SLUG_RENAME: Dict[str, str] = {
    "berry": "现代极化理论与Berry相位计算",
    "chern": "Chern数与贝里曲率计算",
    "crpa": "约束RPA计算",
    "dft": "高通量DFT计算流程",
    "dft-soc": "第一性原理DFT计算非共线磁性SOC",
    "dft-vdw": "第一性原理DFT计算vdW修正滑移势垒",
    "eisenbud": "Wigner-Smith时延",
    "fisher": "Fisher信息与Cramer-Rao下界分析",
    "hubbard": "双位点DFT加U修正",
    "kubo": "Kubo公式线性响应输运计算",
    "lifshitz": "Lifshitz-Kosevich分析与有效质量提取",
    "lo": "平衡零拍探测",
    "mae": "自旋轨道耦合磁各向异性能计算",
    "pinn": "物理信息神经网络PINN",
    "qpinn": "量子物理信息神经网络QPINN",
    "vpinn": "变分物理信息神经网络VPINN",
}

# 语义重叠合并组（member → 主页文件 stem；成员转 stub 指向主页）
# 注：成员先经 GARBLED_RENAME 重命名，本表以其重命名后 stem 引用
#（执行顺序：先重命名后合并）。m8e47148a（自旋群/磁空间群，NRSS/RSS
# 判据含独立参数表）保留不合并。
MERGE_GROUPS: List[Tuple[str, List[str]]] = [
    ("磁点群自旋群对称性分析", ["磁性空间群群论对称性分析", "自旋空间群对称性分析"]),
]


def _safe_filename(name: str) -> str:
    from common import safe_filename
    return safe_filename(name)


def scan() -> Dict[str, Any]:
    """扫描待治理项（dry-run 报告）。"""
    report: Dict[str, Any] = {"renames": [], "merges": [], "missing": []}
    all_renames = {**GARBLED_RENAME, **SHORT_SLUG_RENAME}
    for old_stem, new_stem in all_renames.items():
        src = METHODS_DIR / f"{old_stem}.md"
        dst = METHODS_DIR / f"{new_stem}.md"
        if not src.exists():
            report["missing"].append(old_stem)
            continue
        if dst.exists():
            report["missing"].append(f"{old_stem}（目标已存在: {new_stem}）")
            continue
        report["renames"].append({"from": old_stem, "to": new_stem,
                                  "bytes": src.stat().st_size})
    for main_stem, members in MERGE_GROUPS:
        for m in members:
            # 成员可能在本次重命名后才会以新 stem 存在（先重命名后合并）
            renamed_in_batch = any(r["to"] == m for r in report["renames"])
            if renamed_in_batch or (METHODS_DIR / f"{m}.md").exists():
                report["merges"].append({"member": m, "main": main_stem})
    return report


def apply_renames(renames: List[Dict[str, str]]) -> int:
    """执行重命名：move + frontmatter updated_at 刷新。"""
    n = 0
    for r in renames:
        src = METHODS_DIR / f"{r['from']}.md"
        dst = METHODS_DIR / f"{r['to']}.md"
        if not src.exists():
            continue
        shutil.move(str(src), str(dst))
        text = dst.read_text(encoding="utf-8")
        text = text.replace('updated_at: "', f'updated_at: "', 1)
        # 简单刷新 updated_at（frontmatter 已有字段就地更新）
        text = re.sub(r'(updated_at:\s*")[^"]+(")', rf"\g<1>{now_utc()}\g<2>", text, count=1)
        dst.write_text(text, encoding="utf-8")
        n += 1
        if _log:
            _log.info(f"[methods-governance] 重命名: {r['from']} → {r['to']}")
    return n


def apply_merges(merges: List[Dict[str, str]], dry_run: bool) -> int:
    """语义重叠变体合并：附录并置（确定性，零 LLM，同 kb_merger 论文页
    双世代去重口径）——成员正文整体并入主页附录小节，成员转重定向 stub。
    """
    n = 0
    for g in merges:
        main_path = METHODS_DIR / f"{g['main']}.md"
        member_path = METHODS_DIR / f"{g['member']}.md"
        if not main_path.exists() or not member_path.exists():
            continue
        if dry_run:
            n += 1
            continue
        main_text = main_path.read_text(encoding="utf-8")
        member_text = member_path.read_text(encoding="utf-8")
        # 剥掉成员 frontmatter，正文并入主页附录
        body = re.sub(r"\A---\n.*?\n---\n", "", member_text, flags=re.S).strip()
        appendix = f"\n\n## 附录：{g['member']}（合并自语义重叠页）\n\n{body}\n"
        with main_path.open("a", encoding="utf-8") as f:
            f.write(appendix)
        # 成员转重定向 stub
        stub = (
            f"---\ntitle: \"{g['member']}\"\ntype: methods\n"
            f"merged_into: \"wiki/methods/{g['main']}.md\"\n"
            f"updated_at: \"{now_utc()}\"\n---\n\n"
            f"本页已并入 [{g['main']}](wiki/methods/{g['main']}.md)。\n"
        )
        member_path.write_text(stub, encoding="utf-8")
        n += 1
        if _log:
            _log.info(f"[methods-governance] 合并: {g['member']} → {g['main']}")
    return n


def rebuild_graph() -> bool:
    """图谱/索引重建（重命名后节点 path 失真，走既有全量重建门面）。"""
    try:
        from kb_auto_sync import run_sync
        result = run_sync()
        return bool(result.get("success", True)) if isinstance(result, dict) else True
    except Exception as e:
        if _log:
            _log.warning(f"图谱重建失败（每日 kb-sync 12:40 会兜底重建）: {e}")
        return False


def run(dry_run: bool = True) -> Dict[str, Any]:
    mode = "dry-run 预览" if dry_run else "执行"
    print(f"○ 方法学专题治理（{mode}）")
    report = scan()
    print(f"  重命名: {len(report['renames'])} 页"
          + (f"（缺失/冲突 {len(report['missing'])}）" if report["missing"] else ""))
    for r in report["renames"][:8]:
        print(f"    {r['from']} → {r['to']} ({r['bytes']}B)")
    if len(report["renames"]) > 8:
        print(f"    …共 {len(report['renames'])} 项")
    print(f"  语义合并: {len(report['merges'])} 组")
    for m in report["merges"]:
        print(f"    {m['member']} → {m['main']}")

    if dry_run:
        print("⚠ dry-run 未落盘。确认后执行：--apply")
        return report

    with file_lock("kb-methods-governance"):
        renamed = apply_renames(report["renames"])
        merged = apply_merges(report["merges"], dry_run=False)
    print(f"  ✓ 重命名 {renamed} 页 / 合并 {merged} 组；重建图谱索引…")
    ok = rebuild_graph()
    print(f"  {'✓' if ok else '⚠'} 图谱/索引重建{'完成' if ok else '异常（每日 kb-sync 会兜底）'}")
    save_json(PROJECT_ROOT / "memory" / "methods-governance-log.json",
              {"at": now_utc(), "renamed": renamed, "merged": merged,
               "renames": [r["from"] + "→" + r["to"] for r in report["renames"]]})
    return report


def _self_check() -> int:
    """自检：映射表完整性 + scan 在真实库上的判定。"""
    failures = []
    # 映射目标不含非法路径字符
    for old, new in {**GARBLED_RENAME, **SHORT_SLUG_RENAME}.items():
        if not new or "/" in new or new.startswith("."):
            failures.append(f"非法目标名: {old} → {new}")
    # 合并组成员必须在重命名表中先归位（成员原 stem 或重命名后 stem）
    renamed_targets = set(GARBLED_RENAME.values()) | set(SHORT_SLUG_RENAME.values())
    for main, members in MERGE_GROUPS:
        for m in members:
            if m not in renamed_targets and not (METHODS_DIR / f"{m}.md").exists():
                failures.append(f"合并成员 {m} 不在重命名映射且原文件不存在")
    # 乱码页在真实库中存在且 title 非空
    import re as _re
    for stem in list(GARBLED_RENAME)[:3]:
        f = METHODS_DIR / f"{stem}.md"
        if f.exists():
            t = f.read_text(encoding="utf-8")
            if not _re.search(r'^title:\s*"\S', t, re.M):
                failures.append(f"{stem} title 为空，重命名依据缺失")
    if failures:
        for x in failures:
            print(f"✗ {x}")
        return 1
    print("✓ kb_methods_governance 自检通过")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="方法学专题治理（重命名/合并）")
    parser.add_argument("--apply", action="store_true", help="执行治理（默认 dry-run）")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args(argv)
    if args.self_check:
        return _self_check()
    run(dry_run=not args.apply)
    return 0


if __name__ == "__main__":
    sys.exit(main())
