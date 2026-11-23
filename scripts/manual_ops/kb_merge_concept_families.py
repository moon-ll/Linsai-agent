#!/usr/bin/env python3
"""概念家族归并执行器（v6.10.52 一次性修复，2026-09-25 知识库体检产物）。

背景
----
体检发现 concepts/methods 存在同概念变体页并存（kb_merger 的 title
分组与 _entity_key 对"同概念不同标题"变体均失明）：
    - CEP门控 ×5、固体高次谐波 ×4、相对论等离子体镜面 ×4、
      CEP门控 sub-1.5-cycle ×3（methods）
    - 跨类型重复：concepts/高次谐波产生 vs methods/hhg（title 即
      "高次谐波产生（HHG）"，571+258 条入链分裂在两页）
    - 跨类型重复：concepts/波形控制（lightwave control） vs methods/波形控制

处置原则
--------
1. 显式映射（本文件内 CURATED_GROUPS），不靠自动检测——概念归并必须
   人工审定，误并比重复更难恢复。
2. LLM 融合正文（merge_pair use_llm=True），失败自动降级附录并置。
3. 合并后收集 {旧title: 新title} 全库改写引用（related + wikilink）。
4. 全部写入走 kb_merger.merge_pair / kb_wiki 门面，stub 留检索可达性。

用法
----
    python3 scripts/manual_ops/kb_merge_concept_families.py --dry-run
    python3 scripts/manual_ops/kb_merge_concept_families.py
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

# 人工审定的归并映射：primary ← [被并页…]
# 依据 2026-09-25 体检 + 逐页标题核对；OAM-CEP 耦合/solid-HHG 三份
# survey 属子主题或索引页，不并。
CURATED_GROUPS = [
    {
        "name": "CEP门控",
        "primary": "wiki/concepts/CEP门控.md",
        "members": [
            "wiki/concepts/CEP门控__Carrier-envelope_phase_gating.md",
            "wiki/concepts/CEP门控_载波包络相位门控.md",
            "wiki/concepts/CEP门控光波脉冲.md",
            "wiki/concepts/CEP门控光波脉冲控制相对论等离子体镜.md",
        ],
    },
    {
        "name": "固体高次谐波",
        "primary": "wiki/concepts/固体高次谐波.md",
        "members": [
            "wiki/concepts/固体高次谐波_Solid-state_HHG.md",
            "wiki/concepts/固体高次谐波_固体HHG.md",
            "wiki/concepts/固体高次谐波产生__Solid-state_HHG.md",
        ],
    },
    {
        "name": "相对论等离子体镜面",
        "primary": "wiki/concepts/相对论等离子体镜面.md",
        "members": [
            "wiki/concepts/相对论等离子体镜面_relativistic_plasma_mirror.md",
            "wiki/concepts/相对论性等离子体镜面__Relativistic_plasma_mirror.md",
            "wiki/concepts/相对论等离子体镜方案产生孤立阿秒脉冲.md",
        ],
    },
    {
        "name": "CEP门控 sub-1.5-cycle 激光脉冲（methods）",
        "primary": "wiki/methods/CEP门控sub-1_5-cycle激光脉冲技术.md",
        "members": [
            "wiki/methods/CEP门控sub-1_5-cycle激光脉冲驱动等离子体镜面.md",
            "wiki/methods/CEP门控sub-1_5-cycle脉冲驱动等离子体镜面.md",
        ],
    },
    {
        "name": "高次谐波产生（跨类型：methods/hhg 并入概念枢纽页）",
        "primary": "wiki/concepts/高次谐波产生.md",
        "members": ["wiki/methods/hhg.md"],
    },
    {
        "name": "波形控制（跨类型：概念变体并入方法页）",
        "primary": "wiki/methods/波形控制.md",
        "members": ["wiki/concepts/波形控制_lightwave_control.md"],
    },
]


def main(dry_run: bool = False) -> int:
    from kb_merger import merge_pair, rewrite_references, _ensure_wired
    from kb_wiki import get_wiki_page

    _ensure_wired()
    title_map: dict = {}
    done, failed = [], []
    for group in CURATED_GROUPS:
        primary = group["primary"]
        for member in group["members"]:
            try:
                r = merge_pair(primary, member, dry_run=dry_run, use_llm=True)
                if not r.get("success"):
                    failed.append((member, r.get("error", "?")))
                    continue
                done.append((primary, member, r.get("mode")))
                pri = get_wiki_page(primary) or {}
                oth = get_wiki_page(member) or {}
                from pathlib import Path as _P
                pri_title = (pri.get("frontmatter") or {}).get("title", _P(primary).stem)
                oth_title = (oth.get("frontmatter") or {}).get("title", _P(member).stem)
                if oth_title != pri_title:
                    title_map[oth_title] = pri_title
            except Exception as e:
                failed.append((member, str(e)))

    refs = {"pages_changed": 0}
    if title_map and not dry_run:
        refs = rewrite_references(title_map)

    print("概念家族归并: %d 对成功, %d 失败%s"
          % (len(done), len(failed), "（dry-run）" if dry_run else ""))
    for p, m, mode in done:
        print("  ✓ %s ← %s [%s]" % (p, m, mode))
    for m, e in failed:
        print("  ✗ %s | %s" % (m, e))
    print("引用改写: %d 页, title_map %d 项" % (refs.get("pages_changed", 0), len(title_map)))
    for old, new in title_map.items():
        print("  ↻ %s → %s" % (old, new))
    return 0 if not failed else 1


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    sys.exit(main(dry_run=dry))
