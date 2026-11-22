#!/usr/bin/env python3
"""kb_repair_frontmatter_clobber.py — 修复 literature_service.link_to_proposal
造成的 wiki 页面 frontmatter 覆盖损坏（v7.3.6）。

背景（2026-11-03 20h 健康检查实证）：

`link_to_proposal` 旧实现取 `existing.get("meta", {})` 与
`existing.get("content", "")`，而 `kb_wiki.get_wiki_page` 实际返回键为
`"frontmatter"` / `"body"` → 恒取空值。回写时 `kw_build` 用默认模板重建
整页：

- `created` 被重置为当前时间
- `source_raw` / `tags` / `growth_stage` / `confidence` 退化为默认值
- `title` 退化为裸 arXiv ID
- `used_by_proposals` / `related` 被**替换**（原课题引用丢失）
- 正文 `body` 被清空（save_wiki_page 的防御②会保留旧正文，但
  `kw_build` 传空 content 时正文为空 → 实际由 save_wiki_page 的
  existing_body 兜底保住；frontmatter 侧则被默认值覆盖）

生产实测：wiki/papers 168 页 frontmatter 被改写，其中 148 页 `created`
被重置、13 页 `source_raw` 被清空（溯源链断裂）、7 页 title 退化、
93 页 `used_by_proposals` 丢失原课题引用。

修复口径（逐字段合并，保守不覆盖新值）：

- `created` / `title` / `source_raw` / `tags` / `growth_stage` /
  `confidence`：若当前值是**默认值**（即被覆盖的痕迹）而 HEAD 版本有
  真实值 → 回填 HEAD 值；否则保留当前值
- `used_by_proposals` / `related`：并集（HEAD ∪ 当前），不丢任何一边
- `proposals_citations`：并集（dict 形态归一后）
- `status_history`：并集（list 形态归一后）
- 正文 body：保留当前版本（可能含新增的阅读笔记），仅当当前正文为空
  而 HEAD 有正文时才回填

用法：
    python3 scripts/manual_ops/kb_repair_frontmatter_clobber.py --dry-run
    python3 scripts/manual_ops/kb_repair_frontmatter_clobber.py --apply
    python3 scripts/manual_ops/kb_repair_frontmatter_clobber.py --self-check

规范：
    - 仅使用 Python 3 标准库
    - 幂等：重复运行无操作
    - 写回走 kb_wiki.save_wiki_page 门面（图谱/索引同步）
"""

from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from paths import KNOWLEDGE_DIR  # noqa: E402
from kb_text import parse_frontmatter, build_frontmatter  # noqa: E402


# kb_wiki.build_wiki_page 的默认 meta（被覆盖的判定基准）
_DEFAULTS: Dict[str, str] = {
    "tags": "[]",
    "source_raw": '""',
    "growth_stage": '"seedling"',
    "confidence": "0.5",
}

# 允许并集合并的列表字段
_MERGE_LIST_FIELDS = ("used_by_proposals", "related", "tags")

# 允许并集合并的 dict 字段（序列化后可能是字符串形态）
_MERGE_DICT_FIELDS = ("proposals_citations",)


def _git_head_text(rel_path: str) -> Optional[str]:
    """取 HEAD 版本的文件文本；文件未被跟踪或不存在时返回 None。"""
    try:
        res = subprocess.run(
            ["git", "show", f"HEAD:{rel_path}"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
    except Exception:
        return None
    if res.returncode != 0 or not res.stdout:
        return None
    return res.stdout


def _split_fm(text: str) -> Tuple[Dict[str, Any], str]:
    """拆 frontmatter 与正文（兼容双 frontmatter：取外层 + 内层合并）。"""
    fm, body = parse_frontmatter(text)
    if body.lstrip().startswith("---"):
        inner_fm, inner_body = parse_frontmatter(body)
        if inner_fm:
            merged = dict(fm)
            merged.update(inner_fm)
            # created 取更早者
            c_out = str(fm.get("created", ""))
            c_in = str(inner_fm.get("created", ""))
            if c_out and (not c_in or c_out < c_in):
                merged["created"] = c_out
            return merged, inner_body
    return fm, body


def _as_list(value: Any) -> List[Any]:
    """把 frontmatter 里的列表值归一为 list。"""
    if value is None:
        return []
    if isinstance(value, list):
        return list(value)
    if isinstance(value, str):
        s = value.strip()
        if s.startswith("["):
            try:
                parsed = ast.literal_eval(s)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
        return [s.strip('"')] if s.strip('"') else []
    return [value]


def _as_dict(value: Any) -> Dict[str, Any]:
    """把 frontmatter 里的 dict 值归一为 dict（序列化字符串形态还原）。"""
    if value is None:
        return {}
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, str):
        try:
            parsed = ast.literal_eval(value)
        except Exception:
            return {}
        if isinstance(parsed, dict):
            return parsed
    return {}


def _dedup(items: List[Any]) -> List[Any]:
    """保序去重。"""
    seen = set()
    out = []
    for it in items:
        try:
            key = it if isinstance(it, (str, int, float, bool, type(None))) else repr(it)
        except Exception:
            key = repr(it)
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def plan_repair(head_fm: Dict[str, Any], cur_fm: Dict[str, Any]) -> Dict[str, Any]:
    """计算单页修复方案（纯函数，不写盘）。

    Returns:
        {"meta": {...需改的字段...}, "actions": [...]}
    """
    actions: List[str] = []
    meta: Dict[str, Any] = {}

    # ① 标量字段：当前值是默认值（被覆盖痕迹）且 HEAD 有真实值 → 回填
    for key, default_literal in _DEFAULTS.items():
        cur = cur_fm.get(key)
        head = head_fm.get(key)
        if head is None or cur is None:
            continue
        cur_s = _literal(cur)
        if cur_s == default_literal and _literal(head) != default_literal:
            meta[key] = head
            actions.append(f"回填 {key}: {default_literal} → {_literal(head)[:50]}")

    # title：当前值退化为裸 arXiv ID 且 HEAD 有真实题名 → 回填
    cur_title = str(cur_fm.get("title", "")).strip()
    head_title = str(head_fm.get("title", "")).strip()
    if head_title and cur_title != head_title:
        cur_stem = re.fullmatch(r"(?:Paper:\s*)?(\d{4}\.\d{4,5})", cur_title)
        if cur_stem and not re.fullmatch(r"(?:Paper:\s*)?(\d{4}\.\d{4,5})", head_title):
            meta["title"] = head_title
            actions.append(f"回填 title: {cur_title[:30]} → {head_title[:40]}")

    # created：当前值晚于 HEAD 值 → 取更早者（HEAD 是真实创建时间）
    cur_created = str(cur_fm.get("created", "")).strip()
    head_created = str(head_fm.get("created", "")).strip()
    if cur_created and head_created and cur_created > head_created:
        meta["created"] = head_created
        actions.append(f"回填 created: {cur_created} → {head_created}")

    # ② 列表字段：并集（集合语义——顺序不同但元素相同视为无变化，保证幂等）
    for key in _MERGE_LIST_FIELDS:
        head_items = _as_list(head_fm.get(key))
        cur_items = _as_list(cur_fm.get(key))
        if not head_items:
            continue
        merged = _dedup(head_items + cur_items)
        if set(map(repr, merged)) != set(map(repr, cur_items)):
            meta[key] = merged
            actions.append(f"并集 {key}: {len(cur_items)} → {len(merged)} 项")

    # ③ dict 字段：并集
    for key in _MERGE_DICT_FIELDS:
        head_d = _as_dict(head_fm.get(key))
        cur_d = _as_dict(cur_fm.get(key))
        if not head_d:
            continue
        merged = dict(head_d)
        for pid, cites in cur_d.items():
            merged[pid] = _dedup(list(merged.get(pid, [])) + list(_as_list(cites)))
        if set(merged.keys()) != set(cur_d.keys()) or any(
            set(map(repr, _as_list(merged[k]))) != set(map(repr, _as_list(cur_d[k])))
            for k in cur_d
        ):
            meta[key] = merged
            actions.append(f"并集 {key}: {len(cur_d)} → {len(merged)} 个课题")

    return {"meta": meta, "actions": actions}


def _literal(value: Any) -> str:
    """把 frontmatter 值转成与 build_frontmatter 输出一致的字面量。"""
    if isinstance(value, list):
        return "[" + ", ".join(f'"{v}"' for v in value) + "]"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return '"' + str(value).replace('"', '\\"') + '"'


def repair(dry_run: bool = True, apply: bool = False) -> Dict[str, Any]:
    """扫描 knowledge/wiki/papers 并修复被覆盖的 frontmatter。

    Args:
        dry_run: 仅预览
        apply: 实际写盘
    Returns:
        统计摘要
    """
    import knowledge_base  # noqa: F401  （注入门面依赖）
    from kb_wiki import save_wiki_page

    stats = {
        "scanned": 0,
        "repaired": 0,
        "actions": 0,
        "errors": 0,
        "files": [],
    }

    papers_dir = KNOWLEDGE_DIR / "wiki" / "papers"
    if not papers_dir.exists():
        print("✗ wiki/papers 目录不存在")
        return stats

    for f in sorted(papers_dir.glob("*.md")):
        rel = f"wiki/papers/{f.name}"
        git_rel = f"knowledge/{rel}"
        stats["scanned"] += 1
        try:
            head_text = _git_head_text(git_rel)
            if head_text is None:
                continue  # 未被 git 跟踪（新页）→ 无基线可比
            head_fm, _head_body = _split_fm(head_text)
            cur_text = f.read_text(encoding="utf-8")
            cur_fm, cur_body = _split_fm(cur_text)

            plan = plan_repair(head_fm, cur_fm)
            if not plan["meta"]:
                continue

            stats["repaired"] += 1
            stats["actions"] += len(plan["actions"])
            stats["files"].append(f.name)
            print(f"  ✓ {f.name}")
            for a in plan["actions"]:
                print(f"      {a}")

            if apply:
                merged = dict(cur_fm)
                merged.update(plan["meta"])
                save_wiki_page(rel, cur_body, meta=merged)
        except Exception as e:
            stats["errors"] += 1
            print(f"  ✗ {f.name}: {e}")

    return stats


def _self_check() -> bool:
    """自检：构造被覆盖夹具，验证回填/并集逻辑。"""
    ok = True

    head_fm = {
        "title": "Singular high-harmonic transport above a quantum threshold",
        "type": "papers",
        "created": "2026-09-21T15:00:37Z",
        "tags": ["deepxiv-论文库", "深度解析"],
        "source_raw": "papers/2026-2609.20990-singular.md",
        "growth_stage": "growing",
        "confidence": 0.8,
        "used_by_proposals": ["general-ssh-weyl-20260920"],
        "related": ["arpes", "拓扑绝缘体"],
        "proposals_citations": "{'general-ssh-weyl-20260920': ['adversarial-review']}",
    }
    # 模拟被 link_to_proposal 覆盖后的状态
    cur_fm = {
        "title": "2609.20990",
        "type": "papers",
        "created": "2026-11-02T16:50:46Z",
        "tags": [],
        "source_raw": "",
        "growth_stage": "seedling",
        "confidence": 0.5,
        "used_by_proposals": ["general-moire-strong-field-probe-20260726"],
        "related": ["arpes"],
        "proposals_citations": "{'general-moire-strong-field-probe-20260726': ['adversarial-review']}",
    }

    plan = plan_repair(head_fm, cur_fm)
    m = plan["meta"]

    def check(cond: bool, msg: str) -> None:
        nonlocal ok
        if not cond:
            print(f"  ✗ {msg}")
            ok = False

    check(m.get("source_raw") == head_fm["source_raw"], "source_raw 未回填")
    check(m.get("tags") == head_fm["tags"], "tags 未回填")
    check(m.get("growth_stage") == "growing", "growth_stage 未回填")
    check(m.get("confidence") == 0.8, "confidence 未回填")
    check(m.get("created") == "2026-09-21T15:00:37Z", "created 未回填更早值")
    check(m.get("title") == head_fm["title"], "title 未回填真实题名")
    check(
        set(m.get("used_by_proposals", []))
        == {"general-ssh-weyl-20260920", "general-moire-strong-field-probe-20260726"},
        f"used_by_proposals 未并集（实际 {m.get('used_by_proposals')!r}）",
    )
    check(
        set(m.get("related", [])) == {"arpes", "拓扑绝缘体"},
        f"related 未并集（实际 {m.get('related')!r}）",
    )
    check(
        set(m.get("proposals_citations", {}))
        == {"general-ssh-weyl-20260920", "general-moire-strong-field-probe-20260726"},
        f"proposals_citations 未并集（实际 {m.get('proposals_citations')!r}）",
    )

    # 幂等：修复后再算一次应无改动
    merged = dict(cur_fm)
    merged.update(m)
    plan2 = plan_repair(head_fm, merged)
    check(not plan2["meta"], f"幂等性失效（第二轮仍有改动 {plan2['meta']!r}）")

    # 未被覆盖的页不应产生改动
    plan3 = plan_repair(head_fm, dict(head_fm))
    check(not plan3["meta"], "未被覆盖的页被误判为需修复")

    if ok:
        print("  ✓ 回填/并集/幂等/不误伤 全部通过")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(
        description="修复 link_to_proposal 造成的 wiki frontmatter 覆盖损坏"
    )
    parser.add_argument("--dry-run", action="store_true", help="仅预览（默认）")
    parser.add_argument("--apply", action="store_true", help="实际修复写盘")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args()

    if args.self_check:
        passed = _self_check()
        print(("✓" if passed else "✗") + " kb_repair_frontmatter_clobber 自检")
        return 0 if passed else 1

    print("=" * 60)
    print("◐ kb_repair_frontmatter_clobber" + ("（--apply 执行修复）" if args.apply else "（dry-run 预览）"))
    print("=" * 60)

    stats = repair(dry_run=not args.apply, apply=args.apply)
    print("-" * 60)
    print(
        f"扫描 {stats['scanned']} 页 | 需修复 {stats['repaired']} 页 | "
        f"字段动作 {stats['actions']} 个 | 错误 {stats['errors']}"
    )
    if not args.apply:
        print("提示：加 --apply 执行实际修复")
    return 0 if stats["errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
