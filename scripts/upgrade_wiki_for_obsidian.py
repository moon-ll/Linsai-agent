#!/usr/bin/env python3
"""
一次性升级脚本：为现有 wiki 文件注入 Obsidian 双向链接。

用法:
    cd /Users/ll/Desktop/LinSai-CoPilot
    python3 scripts/upgrade_wiki_for_obsidian.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import knowledge_base as kb


def main() -> None:
    print("🚀 开始升级 wiki 文件以兼容 Obsidian...")
    wiki_dir = kb.WIKI_DIR
    if not wiki_dir.exists():
        print("✗ 找不到 wiki 目录")
        return

    count = 0
    for fpath in sorted(wiki_dir.rglob("*.md")):
        try:
            text = fpath.read_text(encoding="utf-8")
            # 跳过没有 frontmatter 的文件
            if not text.strip().startswith("---"):
                continue
            # 注入 wikilinks
            new_text = kb._inject_wikilinks(text)
            if new_text != text:
                fpath.write_text(new_text, encoding="utf-8")
                rel = fpath.relative_to(kb.KNOWLEDGE_DIR)
                print(f"  ✓ 已更新: {rel}")
                count += 1
            else:
                rel = fpath.relative_to(kb.KNOWLEDGE_DIR)
                print(f"  ○ 无变化: {rel}")
        except Exception as e:
            print(f"  ✗ 失败: {fpath} — {e}")

    print(f"\n✅ 完成，共更新 {count} 个文件")
    print("💡 提示：现在可以将 knowledge/ 目录作为 Obsidian Vault 打开")


if __name__ == "__main__":
    main()
