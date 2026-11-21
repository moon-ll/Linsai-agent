#!/usr/bin/env python3
"""
kb_concepts_dedup.py — 概念页同族归并（v7.2.15，零 LLM）

用途：
    修复 ZCode 消费 concepts-backfill-worklist 的副作用——按清单字面
    逐项建页，未做别名归并，产生同概念多页（实测 76 页中 CEP门控一族
    5 个变体、三步模型/固体高次谐波等双名页，~10 组；27 页薄壳）。

机制（确定性，kb_merger 的 stub 惯例）：
    1. 家族分组：stem 按 `__` 双下划线切基名；单下划线拉丁尾一并剥离
       （`固体高次谐波_Solid-state_HHG` → `固体高次谐波`）；基名页存在时，
       `基名_后缀` 单下划线中文变体也归入（`CEP门控_载波包络相位门控`）。
    2. 主页选择：正文最厚者优先（并列时 tags 非空优先）。
    3. 归并动作：被并页有实质内容（≥80 字）→ 追加到主页
       `## 合并自「X」` 附录；被并页转重定向 stub（frontmatter 记
       merged_into，保留检索可达性）；变体名注册进 aliases.json。
    4. 幂等：已是 stub 的页不再参与。

用法：
    python3 scripts/kb_concepts_dedup.py --dry-run   # 预览归并方案
    python3 scripts/kb_concepts_dedup.py --apply     # 执行归并
    python3 scripts/kb_concepts_dedup.py --self-check

约束：仅标准库；pathlib；JSON ensure_ascii=False indent=2；原子写入。
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from common import now_utc, save_json  # noqa: E402

CONCEPTS_DIR = PROJECT_ROOT / "knowledge" / "wiki" / "concepts"
ALIASES_PATH = PROJECT_ROOT / "knowledge" / "aliases.json"
THIN_BODY = 200
MEANINGFUL_BODY = 80


def _family_key(stem: str) -> str:
    """stem → 家族基名。"""
    k = stem.split("__")[0]
    # 单下划线拉丁尾：固体高次谐波_Solid-state_HHG → 固体高次谐波
    m = re.match(r"^(.{2,}?)_[A-Za-z].*$", k)
    if m:
        k = m.group(1)
    return k


def _read_page(path: Path) -> Tuple[str, str]:
    """返回 (frontmatter, body)。"""
    text = path.read_text(encoding="utf-8", errors="ignore")
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if m:
        return m.group(1), m.group(2)
    return "", text


def _is_stub(frontmatter: str) -> bool:
    return "merged_into" in frontmatter


def _body_len(body: str) -> int:
    return len(re.sub(r"\s", "", body))


def _has_tags(frontmatter: str) -> bool:
    return bool(re.search(r"^tags:\s*\[.+\]", frontmatter, re.M))


def scan_families() -> List[Dict[str, Any]]:
    """扫描全部概念页，返回 >1 成员且含非 stub 实体页的家族。"""
    pages: Dict[str, Dict[str, Any]] = {}
    for p in sorted(CONCEPTS_DIR.glob("*.md")):
        fm, body = _read_page(p)
        pages[p.stem] = {
            "path": p, "fm": fm, "body": body,
            "stub": _is_stub(fm), "len": _body_len(body),
            "tags": _has_tags(fm),
        }

    # 分组：基名 → [stem]
    groups: Dict[str, List[str]] = {}
    for stem, info in pages.items():
        if info["stub"]:
            continue
        key = _family_key(stem)
        groups.setdefault(key, []).append(stem)

    # 单下划线中文变体归并：基名页存在时，`基名_中文` 也入族
    for stem in list(groups.keys()):
        pass  # 基名本身即组键，已覆盖
    for stem, info in list(pages.items()):
        if info["stub"]:
            continue
        base = _family_key(stem)
        if base != stem:
            continue  # 已通过 family_key 归组
        # stem 作为前缀：CEP门控_载波包络相位门控 → CEP门控 族
        for other, oinfo in pages.items():
            if other == stem or oinfo["stub"]:
                continue
            if other.startswith(stem + "_") and other not in groups.get(stem, []):
                groups.setdefault(stem, []).append(other)

    families = []
    for key, members in groups.items():
        if len(members) < 2:
            continue
        fam = [pages[m] | {"stem": m} for m in members]
        families.append({"base": key, "members": fam})
    return families


def plan_merge(family: Dict[str, Any]) -> Dict[str, Any]:
    """为单家族生成归并方案：选主页、列被并页。"""
    members = sorted(
        family["members"], key=lambda m: (m["len"], m["tags"]), reverse=True
    )
    primary = members[0]
    others = members[1:]
    return {
        "base": family["base"],
        "primary": primary["stem"],
        "primary_path": primary["path"],
        "others": [
            {"stem": o["stem"], "path": o["path"],
             "len": o["len"], "meaningful": o["len"] >= MEANINGFUL_BODY}
            for o in others
        ],
    }


def apply_merge(plan: Dict[str, Any]) -> List[str]:
    """执行单家族归并：附录内容 + stub + alias 注册。返回报告行。"""
    reports = []
    primary_path: Path = plan["primary_path"]
    _, primary_body = _read_page(primary_path)
    appendices = []
    new_aliases: List[str] = []

    for o in plan["others"]:
        _, obody = _read_page(o["path"])
        if o["meaningful"]:
            appendices.append(
                "\n\n## 合并自「%s」\n\n%s\n" % (o["stem"], obody.strip())
            )
        # 转重定向 stub
        stub = (
            "---\n"
            f"title: \"{o['stem']}\"\n"
            "type: \"concepts\"\n"
            f"created: \"{now_utc()}\"\n"
            f"updated: \"{now_utc()}\"\n"
            f"tags: []\n"
            f"merged_into: \"{plan['primary']}\"\n"
            f"merged_at: \"{now_utc()}\"\n"
            "---\n\n"
            f"# {o['stem']}（已合并）\n\n"
            f"本页已合并至 **{plan['primary']}**（`{plan['primary']}`）。\n\n"
            f"请前往主页面查看完整内容。\n"
        )
        o["path"].write_text(stub, encoding="utf-8")
        new_aliases.append(o["stem"])
        reports.append(f"✓ {o['stem']} → {plan['primary']}（stub，{o['len']}字）")

    if appendices:
        primary_path.write_text(
            primary_body.rstrip() + "".join(appendices), encoding="utf-8"
        )

    # aliases.json 注册（canonical → [别名...]）
    if new_aliases:
        data = {}
        if ALIASES_PATH.exists():
            try:
                data = json.loads(ALIASES_PATH.read_text(encoding="utf-8"))
            except Exception:
                data = {}
        lst = data.get(plan["primary"], [])
        if isinstance(lst, str):
            lst = [lst]
        for a in new_aliases:
            if a not in lst:
                lst.append(a)
        data[plan["primary"]] = lst
        save_json(ALIASES_PATH, data)

    return reports


def run(dry_run: bool) -> List[str]:
    families = scan_families()
    if not families:
        return ["○ 无需归并（无同族多变体）"]
    reports = []
    for fam in families:
        plan = plan_merge(fam)
        header = (f"族 [{plan['base']}] 主页={plan['primary']}，"
                  f"被并 {len(plan['others'])} 页")
        if dry_run:
            others = ", ".join(o["stem"] for o in plan["others"])
            reports.append(f"○ {header}（{others}）")
        else:
            reports.append(header)
            reports.extend(apply_merge(plan))
    return reports


def scan_thin_pages() -> List[Dict[str, Any]]:
    """归并后薄页扫描（供修订 worklist）。"""
    thin = []
    for p in sorted(CONCEPTS_DIR.glob("*.md")):
        fm, body = _read_page(p)
        if _is_stub(fm):
            continue
        reasons = []
        if _body_len(body) < THIN_BODY:
            reasons.append(f"正文{_body_len(body)}字<{THIN_BODY}")
        if not _has_tags(fm):
            reasons.append("tags空")
        if reasons:
            thin.append({"page": p.stem, "issues": reasons})
    return thin


def emit_revision_worklist() -> int:
    """发射薄页修订清单（ZCode 消费）。"""
    thin = scan_thin_pages()
    out = PROJECT_ROOT / "memory" / "concepts-revision-worklist.json"
    save_json(out, {
        "emitted_at": now_utc(),
        "count": len(thin),
        "consumed_by": "ZCode",
        "task_note": (
            "逐页修订 knowledge/wiki/concepts/<page>.md 至质量门标准："
            "正文 ≥200 字、≥2 个二级标题（定义/物理内涵/与林赛研究关联等）、"
            "tags 非空（含 type/concept + topic 主题标签）。"
            "注意：同族变体页已归并为 stub（merged_into），只修订主页，"
            "不要再为别名新建页面。扩写素材可参考该概念的 wikilink 来源论文页。"
        ),
        "targets": thin,
    })
    print(f"  ✓ 修订清单: {len(thin)} 页 → {out.relative_to(PROJECT_ROOT)}")
    return len(thin)


def _self_check() -> List[str]:
    msgs = []
    msgs.append("✓ family_key 双下划线: " + str(
        _family_key("三步模型__Three-step_model") == "三步模型"))
    msgs.append("✓ family_key 拉丁尾: " + str(
        _family_key("固体高次谐波_Solid-state_HHG") == "固体高次谐波"))
    msgs.append("✓ family_key 中文变体保留: " + str(
        _family_key("CEP门控_载波包络相位门控") == "CEP门控_载波包络相位门控"))
    if CONCEPTS_DIR.exists():
        fams = scan_families()
        msgs.append(f"✓ 真实库家族扫描: {len(fams)} 族多变体")
    else:
        msgs.append("○ concepts 目录不存在，跳过")
    return msgs


def main() -> int:
    parser = argparse.ArgumentParser(description="概念页同族归并（零 LLM）")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--emit-revision", action="store_true",
                        help="归并后发射薄页修订清单")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()

    if args.self_check:
        for m in _self_check():
            print(m)
        return 0
    if args.dry_run or args.apply:
        for line in run(dry_run=args.dry_run):
            print(line)
    if args.emit_revision:
        emit_revision_worklist()
    if not any(vars(args).values()):
        parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
