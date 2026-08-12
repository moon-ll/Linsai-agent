#!/usr/bin/env python3
"""repair_frontmatter.py — 修复知识库 wiki/papers 笔记的 frontmatter 类型损坏。

问题：外部重格式化工具将 YAML frontmatter 中的列表和数字错误地
引号包裹，导致 parse_frontmatter 将其解析为字符串而非原生类型。
  - confidence: "0.5"  → 应为 0.5 (float)
  - tags: "[]"          → 应为 [] (list)
  - used_by_proposals: "["x"]" → 应为 ["x"] (list)

修复策略：
  1. 用仓库 parse_frontmatter 解析
  2. 对白名单字段的字符串值尝试类型恢复
  3. 用仓库 build_frontmatter 正确回写
  4. body 保持不变

用法示例：
    python3 scripts/repair_frontmatter.py --dry-run   # 预览修复内容
    python3 scripts/repair_frontmatter.py             # 执行修复
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from kb_text import parse_frontmatter, build_frontmatter

WIKI_PAPERS_DIR = PROJECT_ROOT / "knowledge" / "wiki" / "papers"

# 需要恢复类型的字段白名单。
# 仅对这些已知类型的字段执行 json.loads 类型恢复，
# 避免 arxiv_id/title 等字符串被误识别为 float。
_LIST_FIELDS = {"tags", "related", "used_by_proposals", "project"}
_NUMERIC_FIELDS = {"confidence"}


def _try_recover_type(key: str, value):
    """对指定字段的字符串值尝试恢复原生类型。

    - 列表字段："[]" → [], '["x"]' → ["x"]
    - 数字字段："0.5" → 0.5
    - 其他字段：原样返回
    """
    if not isinstance(value, str):
        return value  # 已经是非字符串类型，无需处理
    if key in _LIST_FIELDS:
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, ValueError):
            pass
        return value
    if key in _NUMERIC_FIELDS:
        try:
            return float(value)
        except (ValueError, TypeError):
            pass
        return value
    return value


def repair_note(filepath: Path, dry_run: bool = False) -> dict:
    """修复单篇笔记的 frontmatter。

    Returns:
        {"file": str, "fixed": list[str], "error": str|None}
    """
    result = {"file": filepath.name, "fixed": [], "error": None}
    try:
        text = filepath.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        if not fm:
            result["error"] = "无 frontmatter"
            return result

        new_fm = {}
        fixed_fields = []
        for key, val in fm.items():
            recovered = _try_recover_type(key, val)
            if recovered is not val and type(recovered) != type(val):
                fixed_fields.append(f"{key}: {type(val).__name__} → {type(recovered).__name__}")
            new_fm[key] = recovered

        if not fixed_fields:
            result["fixed"] = []
            return result

        result["fixed"] = fixed_fields

        if dry_run:
            return result

        # 用 build_frontmatter 正确回写
        new_fm_text = build_frontmatter(new_fm)
        new_text = f"{new_fm_text}\n\n{body}"
        filepath.write_text(new_text, encoding="utf-8")

    except Exception as e:
        result["error"] = str(e)

    return result


def main():
    dry_run = "--dry-run" in sys.argv

    if not WIKI_PAPERS_DIR.exists():
        print(f"✗ 目录不存在: {WIKI_PAPERS_DIR}")
        sys.exit(1)

    notes = sorted(WIKI_PAPERS_DIR.glob("*.md"))
    print(f"共 {len(notes)} 篇笔记{'（dry-run 模式）' if dry_run else ''}\n")

    total_fixed = 0
    total_errors = 0
    for note in notes:
        r = repair_note(note, dry_run=dry_run)
        if r["error"]:
            print(f"  ✗ {r['file']}: {r['error']}")
            total_errors += 1
        elif r["fixed"]:
            total_fixed += 1
            for f in r["fixed"]:
                print(f"  ✓ {r['file']}: {f}")
        else:
            pass  # 无需修复，静默

    print(f"\n修复 {total_fixed} 篇，跳过 {len(notes) - total_fixed - total_errors} 篇，失败 {total_errors} 篇")

    if dry_run:
        print("（预览模式，未修改任何文件）")


if __name__ == "__main__":
    main()
