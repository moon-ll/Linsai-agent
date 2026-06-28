#!/usr/bin/env python3
"""
wiki_regenerator/run.py — wiki 报告重建主入口
从 knowledge/raw/papers/ 读取真实论文，按模板生成 6 篇 wiki 报告。
"""

import sys
from pathlib import Path
_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
# 确保 scripts/ 在 sys.path 中，以便 import paths
_SCRIPTS_DIR = _SCRIPT_DIR.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

try:  # 包模式优先，脚本模式回退
    from .report_writer import (
        generate_principles_report,
        generate_methods_report,
        generate_systems_report,
        generate_technology_report,
        generate_teams_report,
        generate_comprehensive_report,
    )
    from .paper_reader import load_all_papers
except ImportError:
    from report_writer import (
        generate_principles_report,
        generate_methods_report,
        generate_systems_report,
        generate_technology_report,
        generate_teams_report,
        generate_comprehensive_report,
    )
    from paper_reader import load_all_papers

from paths import PROJECT_ROOT
WIKI_DIR = PROJECT_ROOT / "knowledge" / "wiki" / "papers"
EXISTING_METHODS = WIKI_DIR / "hhg-methods-report.md"


def main():
    print("加载论文...")
    papers = load_all_papers()
    verified = [p for p in papers if p.get("status") == "verified"]
    print(f"  共 {len(papers)} 篇（{len(verified)} 篇 verified）\n")

    WIKI_DIR.mkdir(parents=True, exist_ok=True)
    generated = []

    print("生成报告...")
    for gen_fn, name in [
        (generate_principles_report,  "hhg-principles-report.md"),
        (generate_systems_report,     "hhg-systems-report.md"),
        (generate_technology_report,  "hhg-technology-report.md"),
        (generate_teams_report,       "hhg-teams-report.md"),
        (generate_comprehensive_report,"hhg-comprehensive-report.md"),
    ]:
        try:
            fp = gen_fn(papers, WIKI_DIR)
            generated.append(fp)
            print(f"  ✅ {fp.name}")
        except Exception as e:
            print(f"  ❌ {name}: {e}")

    # hhg-methods-report.md: 保留已有的 §1-4，只追加 §5 + ref
    if EXISTING_METHODS.exists():
        try:
            fp = generate_methods_report(papers, WIKI_DIR, EXISTING_METHODS)
            generated.append(fp)
            print(f"  ✅ {fp.name}（保留 §1-4）")
        except Exception as e:
            print(f"  ❌ hhg-methods-report.md: {e}")
    else:
        print("  ⚠  hhg-methods-report.md 不存在，跳过")

    total_size = sum(fp.stat().st_size for fp in generated)
    print(f"\n完成：{len(generated)} 篇 → {WIKI_DIR}/")
    print(f"总大小：{total_size:,} bytes")


if __name__ == "__main__":
    main()
