#!/usr/bin/env python3
"""
知识库健康修复脚本（kb_health_repair.py）

修复 knowledge/raw/papers/ 目录下论文 frontmatter 的三类问题，
以及删除一个测试残留文件。仅修改 frontmatter 元数据，不改论文正文。

修复内容：
  1. 删除 3 组重复论文文件（每组保留 arxiv 年份正确的一份）。
  2. 为 MOC.md 声明的 5 篇 NSFC 论文补上 project: ["NSFC-强场超快"]。
  3. 清理 2607.xxx 系列论文中被错误标记为 NSFC-强场超快 的 project 字段（改为 []）。
  4. 删除测试残留文件 wiki/projects/NSFC-强场超快/proposals/general-test-kb-20260101.md。

用法：
    python3 kb_health_repair.py --dry-run   # 预览（不写入、不删除）
    python3 kb_health_repair.py --apply     # 执行修复

仅使用 Python 标准库；frontmatter 使用文本/正则替换，不引入 yaml 库。
"""

import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 路径常量
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path("/Users/ll/Desktop/LinSai-CoPilot")
PAPERS_DIR = PROJECT_ROOT / "knowledge" / "raw" / "papers"
TEST_FILE = (
    PROJECT_ROOT
    / "knowledge"
    / "wiki"
    / "projects"
    / "NSFC-强场超快"
    / "proposals"
    / "general-test-kb-20260101.md"
)

# ---------------------------------------------------------------------------
# 待删除的重复论文（保留年份正确的一份，删除冗余的那份）
# ---------------------------------------------------------------------------

DUPLICATES_TO_DELETE = [
    # physics/9906053：保留 1999-（arxiv 真实年份），删除 2024-
    "2024-physics-9906053-Quantum theory of a high harmonic genera.md",
    # 2403.19535：保留 2024-（arxiv 年份），删除 2026-
    "2026-2403.19535-bright-coherent-ultrahigh-harmonics-in-the-kev-x-r.md",
    # 2512.09585：保留 2025-（arxiv 年份），删除 2026-
    "2026-2512.09585-table-top-all-attosecond-transient-absorption-spec.md",
]

# ---------------------------------------------------------------------------
# MOC.md 声明的 5 篇 NSFC 论文 arxiv_id
# ---------------------------------------------------------------------------

NSFC_ARXIV_IDS = [
    "1502.07183",
    "1806.11232",
    "2003.10430",
    "2304.12547",
    "2503.08052",
]

NSFC_PROJECT_VALUE = '["NSFC-强场超快"]'


# ---------------------------------------------------------------------------
# frontmatter 工具函数（纯文本处理，不依赖 yaml 库）
# ---------------------------------------------------------------------------

def split_frontmatter(content):
    """
    将文件内容拆分为 (frontmatter_lines, body_start_index, all_lines)。

    返回:
        fm_lines: list[str]  — frontmatter 内部行（不含首尾 ---）
        fm_end:   int        — 结束 --- 所在的行号
        lines:    list[str]  — 全文行列表

    如果没有 frontmatter，返回 ([], 0, lines)。
    """
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return [], 0, lines

    fm_end = 0
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fm_end = i
            break
    if fm_end == 0:
        return [], 0, lines

    fm_lines = lines[1:fm_end]
    return fm_lines, fm_end, lines


def get_field(fm_lines, field):
    """从 frontmatter 行列表中提取指定字段的原值（含引号）。"""
    pattern = re.compile(r"^" + re.escape(field) + r":\s*(.*)$")
    for line in fm_lines:
        m = pattern.match(line)
        if m:
            return m.group(1)
    return None


def replace_project_line(fm_lines, new_value):
    """
    在 frontmatter 行列表中替换 project 行的值。
    返回 (new_fm_lines, replaced: bool)。
    """
    pattern = re.compile(r"^project:\s*")
    new_fm = list(fm_lines)
    for i, line in enumerate(new_fm):
        if pattern.match(line):
            old = line
            new_fm[i] = f"project: {new_value}"
            return new_fm, True, old
    return new_fm, False, None


# ---------------------------------------------------------------------------
# 扫描函数
# ---------------------------------------------------------------------------

def find_files_by_arxiv_id(target_ids):
    """根据 arxiv_id 列表查找对应的文件路径。返回 {arxiv_id: Path}。"""
    result = {}
    for md_file in sorted(PAPERS_DIR.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        fm_lines, _, _ = split_frontmatter(content)
        if not fm_lines:
            continue
        raw = get_field(fm_lines, "arxiv_id")
        if raw is None:
            continue
        arxiv_id = raw.strip().strip('"').strip("'")
        if arxiv_id in target_ids:
            result[arxiv_id] = md_file
    return result


def find_2607_nsfc_files():
    """
    查找 arxiv_id 以 2607 开头、且 project 字段包含 NSFC-强场超快 的文件。
    返回 [(Path, arxiv_id, old_project_raw), ...]
    """
    result = []
    for md_file in sorted(PAPERS_DIR.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        fm_lines, _, _ = split_frontmatter(content)
        if not fm_lines:
            continue
        raw_id = get_field(fm_lines, "arxiv_id")
        if raw_id is None:
            continue
        arxiv_id = raw_id.strip().strip('"').strip("'")
        if not arxiv_id.startswith("2607"):
            continue
        project_raw = get_field(fm_lines, "project")
        if project_raw and "NSFC-强场超快" in project_raw:
            result.append((md_file, arxiv_id, project_raw.strip()))
    return result


# ---------------------------------------------------------------------------
# 各修复步骤
# ---------------------------------------------------------------------------

def step1_delete_duplicates(dry_run):
    """步骤 1：删除重复论文文件。"""
    print("=" * 70)
    print("步骤 1/4：删除重复论文文件")
    print("=" * 70)
    count = 0
    for name in DUPLICATES_TO_DELETE:
        fpath = PAPERS_DIR / name
        if not fpath.exists():
            print(f"  ○ 跳过（文件不存在）：{name}")
            continue
        if dry_run:
            print(f"  [dry-run] 将删除：{name}")
        else:
            fpath.unlink()
            print(f"  ✓ 已删除：{name}")
        count += 1
    print(f"  -> 共 {'将处理' if dry_run else '已处理'} {count} 个重复文件\n")
    return count


def step2_fix_nsfc_project(dry_run):
    """步骤 2：为 5 篇 NSFC 论文补上 project 字段。"""
    print("=" * 70)
    print('步骤 2/4：为 5 篇 NSFC 论文添加 project: ["NSFC-强场超快"]')
    print("=" * 70)

    found = find_files_by_arxiv_id(NSFC_ARXIV_IDS)
    count = 0

    for arxiv_id in NSFC_ARXIV_IDS:
        if arxiv_id not in found:
            print(f"  ✗ 未找到 arxiv_id={arxiv_id} 的文件！")
            continue
        fpath = found[arxiv_id]
        content = fpath.read_text(encoding="utf-8")
        fm_lines, fm_end, lines = split_frontmatter(content)
        if not fm_lines:
            print(f"  ✗ 无 frontmatter：{fpath.name}")
            continue

        old_project = get_field(fm_lines, "project")
        old_project_clean = (old_project or "").strip()

        # 如果已经是目标值，跳过
        if old_project_clean == NSFC_PROJECT_VALUE:
            print(f"  ○ 跳过（已是目标值）：{fpath.name}  project={old_project_clean}")
            continue

        new_fm, replaced, old_line = replace_project_line(fm_lines, NSFC_PROJECT_VALUE)
        if not replaced:
            # project 字段不存在，插入到 frontmatter 末尾
            if dry_run:
                print(f"  [dry-run] 将新增 project 字段：{fpath.name}")
            else:
                new_fm = list(fm_lines) + [f"project: {NSFC_PROJECT_VALUE}"]
                new_lines = lines[:1] + new_fm + lines[fm_end:]
                fpath.write_text("\n".join(new_lines), encoding="utf-8")
                print(f"  ✓ 已新增 project 字段：{fpath.name}")
            count += 1
            continue

        if dry_run:
            print(f"  [dry-run] 将修改：{fpath.name}")
            print(f"           旧值：project: {old_project_clean}")
            print(f"           新值：project: {NSFC_PROJECT_VALUE}")
        else:
            new_lines = lines[:1] + new_fm + lines[fm_end:]
            fpath.write_text("\n".join(new_lines), encoding="utf-8")
            print(f"  ✓ 已修改：{fpath.name}")
            print(f"           {old_project_clean}  ->  {NSFC_PROJECT_VALUE}")
        count += 1

    print(f"  -> 共 {'将处理' if dry_run else '已处理'} {count} 篇 NSFC 论文\n")
    return count


def step3_fix_2607_project(dry_run):
    """步骤 3：清理 2607.xxx 系列的错误 NSFC 标记。"""
    print("=" * 70)
    print("步骤 3/4：清理 2607.xxx 系列的错误 NSFC 标记（project -> []）")
    print("=" * 70)

    targets = find_2607_nsfc_files()
    if not targets:
        print("  ○ 未发现需要修复的 2607.xxx 文件\n")
        return 0

    count = 0
    for fpath, arxiv_id, old_project in targets:
        content = fpath.read_text(encoding="utf-8")
        fm_lines, fm_end, lines = split_frontmatter(content)
        if not fm_lines:
            print(f"  ✗ 无 frontmatter：{fpath.name}")
            continue

        new_fm, replaced, old_line = replace_project_line(fm_lines, "[]")
        if not replaced:
            print(f"  ✗ 未找到 project 行：{fpath.name}")
            continue

        if dry_run:
            print(f"  [dry-run] 将修改：{fpath.name}  (arxiv_id={arxiv_id})")
            print(f"           旧值：project: {old_project}")
            print(f"           新值：project: []")
        else:
            new_lines = lines[:1] + new_fm + lines[fm_end:]
            fpath.write_text("\n".join(new_lines), encoding="utf-8")
            print(f"  ✓ 已修改：{fpath.name}  (arxiv_id={arxiv_id})")
            print(f"           {old_project}  ->  []")
        count += 1

    print(f"  -> 共 {'将处理' if dry_run else '已处理'} {count} 篇 2607 论文\n")
    return count


def step4_delete_test_file(dry_run):
    """步骤 4：删除测试残留文件。"""
    print("=" * 70)
    print("步骤 4/4：删除测试残留文件")
    print("=" * 70)
    if not TEST_FILE.exists():
        print(f"  ○ 跳过（文件不存在）：{TEST_FILE.name}")
        print()
        return 0
    if dry_run:
        print(f"  [dry-run] 将删除：{TEST_FILE.relative_to(PROJECT_ROOT)}")
    else:
        TEST_FILE.unlink()
        print(f"  ✓ 已删除：{TEST_FILE.relative_to(PROJECT_ROOT)}")
    print()
    return 1


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

def main():
    dry_run = "--apply" not in sys.argv

    if dry_run and "--dry-run" not in sys.argv:
        print("用法: python3 kb_health_repair.py --dry-run | --apply")
        sys.exit(1)

    mode = "DRY-RUN（预览）" if dry_run else "APPLY（实际执行）"
    print(f"\n{'#' * 70}")
    print(f"#  知识库健康修复 — {mode}")
    print(f"#  论文目录: {PAPERS_DIR}")
    print(f"{'#' * 70}\n")

    c1 = step1_delete_duplicates(dry_run)
    c2 = step2_fix_nsfc_project(dry_run)
    c3 = step3_fix_2607_project(dry_run)
    c4 = step4_delete_test_file(dry_run)

    total = c1 + c2 + c3 + c4
    print("=" * 70)
    if dry_run:
        print(f"预览完成：共 {total} 项操作待执行。")
        print("确认无误后请运行: python3 kb_health_repair.py --apply")
    else:
        print(f"修复完成：共执行 {total} 项操作。")
    print("=" * 70)


if __name__ == "__main__":
    main()
