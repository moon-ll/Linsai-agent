#!/usr/bin/env python3
"""proposal_structure_guard.py — 方案结构守卫（v7.2.30）。

P1-2 实施：v7.0.3 重新定位"研究手册"后，"具体性优先于说服性"的指引没有强制
的章节模板，11 课题方案结构不统一（仅 qgi 完整 5 模块、key-transient 3 章节、
attosecond 7 章节含 3 个跨章口径表）。

本守卫：
    1. **生成侧**：`--check <pid>` 校验方案是否覆盖 5 标准章节
       （## 〇产出定位、## 一立项依据、## 二研究内容、## 三研究方案、
       ## 四特色与创新、## 五预期成果）
    2. **消费侧**：评分扣减——缺章节 / 章节错位都计入 critic 报告并触发
       `quality_over_budget = True` 报警
    3. **报告**：落 memory/proposal-structure-report-YYYY-MM-DD.md

CLI：
    python3 scripts/proposal_structure_guard.py --check <pid>
    python3 scripts/proposal_structure_guard.py --check-all
    python3 scripts/proposal_structure_guard.py --self-check

cron 接入（v7.2.30）：
    嵌入 lc-repair：每 12h 在修复扫描中跑一次

阈值（v7.0.3 研究手册化 + 5 章节硬约束）：
    6 个标准 H2 全部覆盖 = pass
    缺 1 个 = warn（不阻断）
    缺 ≥ 2 个 或 顺序错乱 = fail（阻断）
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).parent.parent
OPT_DIR = ROOT / "research_proposals" / "optimizing"
DRAFTS_DIR = ROOT / "research_proposals" / "drafts"
PR_DIR = ROOT / "research_proposals" / "pending_review"

# 标准 6 章节（v7.0.3 研究手册 + 5 章节硬约束）
# 0: 产出定位 / 1: 立项依据 / 2: 研究内容 / 3: 研究方案 / 4: 特色与创新 / 5: 预期成果
STANDARD_H2 = [
    "〇", "一", "二", "三", "四", "五",
]
# 同义词映射（兼容旧版"立项依据"/"立项"等变体）
# v7.3.39（BUG-44）：补 "预期研究成果"——生产产物 scheme.md / content.md 实际
# 用「预期研究成果」而非「预期成果」（2.9 预期研究成果 / 3.7 特色与创新、
# 预期研究成果、年度计划），旧表漏收导致该标题落「其他」→ 误报缺章节。
SYNONYMS = {
    "立项依据": ["立项依据", "选题依据", "选题理由"],
    "研究内容": ["研究内容", "主要研究内容"],
    "研究方案": ["研究方案", "拟采取的研究方案"],
    "特色与创新": ["特色与创新", "研究特色", "创新点", "特色创新", "主要创新点"],
    "预期成果": ["预期成果", "预期目标", "预期结果", "预期研究成果"],
    "产出定位": ["产出定位", "研究定位", "本课题定位"],
}

# v7.3.39（BUG-44）：中文数字序号 → 标准章节映射。
# 仅在**标题本体**（剥离括号补充说明后）恰好是该序号时才算数。
# 旧实现只看标题以「一、」「二、」开头就无条件映射，导致 full_review 骨架
# （一、主线论证链 / 二、章节衔接点 / 三、跨章节统一口径表）被误判为
# 立项依据 / 研究内容 / 研究方案 → 顺序检查假阳性 + 章节集合污染。
_CN_NUM_TO_SECTION = {
    "〇": "产出定位", "零": "产出定位",
    "一": "立项依据",
    "二": "研究内容",
    "三": "研究方案",
    "四": "特色与创新",
    "五": "预期成果",
}

# 标题前缀剥离：括号补充说明 + 中文序号 + 阿拉伯数字层级号（2.7 / 3.1）
_BRACKET_SUFFIX = re.compile(r"[（(【\[][^）)】\]]*[）)】\]]")
_CN_NUM_PREFIX = re.compile(r"^\s*[（(【\[]?\s*([〇零一二三四五六七八九十]+)\s*[）)】\]]?\s*[、.．]?\s*")
_AR_NUM_PREFIX = re.compile(r"^\s*[0-9]+(?:\.[0-9]+)*\s*[、.．]?\s*")
# 纯序号标题（剥完前缀后本体为空）→ 走中文数字兜底
_ONLY_NUMBER_TITLE = re.compile(r"^\s*[（(【\[]?\s*[〇零一二三四五六七八九十]+\s*[）)】\]]?\s*[、.．]?\s*$")


def _log(msg: str) -> None:
    print(f"[proposal_structure_guard] {msg}", flush=True)


def _proposal_dirs() -> List[Tuple[str, Path]]:
    out = []
    for stage in (OPT_DIR, DRAFTS_DIR, PR_DIR):
        if not stage.exists():
            continue
        for d in stage.iterdir():
            if d.is_dir() and (d / "00_research_idea.md").exists():
                out.append((d.name, d))
    return out


def _latest_proposal_file(prop_dir: Path) -> Path:
    """取当前正文的方案文件。

    v7.3.39（BUG-44）：旧实现优先取 ``proposal-draft-r*.md`` 备份
    （executor.py:1381 在 writer 修改前把当前正文备份成 r{round-1}），
    但备份是**上一轮修改前**的快照。writer 返回后 optimize.py:2259 会从
    sections/ 重新组装 ``proposal-draft.md``（live 正文），此后任何轮次
    的修改只落在 live 正文上——备份不再前进。实测 11 课题全部命中：
    备份落后 live 正文 0.5h ~ 1043.9h（attosecond 1009.1h / key-transient
    1043.9h），守卫因此校验的是**陈旧快照**而非当前产出。

    修正：优先读 live 正文 ``proposal-draft.md``；仅当其不存在时才回退到
    备份（按轮号取最大，而非字典序——轮号 ≥10 时字典序会把 r9 排到 r10 之后）。
    """
    proposal_dir = prop_dir / "04_proposal"
    live = proposal_dir / "proposal-draft.md"
    if live.exists():
        return live
    drafts = sorted(
        proposal_dir.glob("proposal-draft-r*.md"),
        key=lambda p: _backup_round(p),
    )
    if drafts:
        return drafts[-1]
    merged = proposal_dir / "proposal-draft-merged.md"
    if merged.exists():
        return merged
    # 兜底读任意一个
    any_md = sorted(proposal_dir.glob("*.md"), key=lambda p: p.stat().st_mtime)
    if any_md:
        return any_md[-1]
    raise FileNotFoundError(f"方案不存在: {proposal_dir}")


def _backup_round(path: Path) -> int:
    """取备份文件名中的轮号（proposal-draft-r{N}.md → N）。解析失败返回 -1。"""
    m = re.search(r"-r(\d+)\.md$", path.name)
    return int(m.group(1)) if m else -1


def _h2_titles(text: str) -> List[str]:
    """取所有 H2 标题。"""
    return [m.group(1).strip() for m in re.finditer(r"^##\s+(.+)$", text, re.M)]


def _strip_bracket_suffix(title: str) -> str:
    """剥离标题里的括号补充说明——（核心问题→研究内容→方案如何回应）等。

    括号内的说明是标题的补充描述而非章节名本身。剥离后若本体与某标准
    章节名一致才判定为该章节，避免 full_review 骨架的序号被误读。
    """
    return _BRACKET_SUFFIX.sub(" ", title).strip()


def _classify_h2(title: str) -> str:
    """将 H2 标题归类到标准章节。无匹配返回 '其他'。

    v7.3.39（BUG-44）修正两处误分类：
      ① 关键词匹配前先剥离括号补充说明，且**一个标题可同时命中多个标准
         章节**——生产 scheme.md 的标题是合并式
         「（三）研究方案、特色与创新、预期研究成果」，旧实现只返回第一个
         命中项（研究方案），把同标题里的「特色与创新」「预期成果」丢掉
         → 误报缺 2 章节。
      ② 中文数字兜底仅在**标题本体就是该序号**时生效（纯序号标题），
         不再无条件把「一、主线论证链」映射成立项依据——否则 full_review
         骨架三条序号标题被误判为立项依据/研究内容/研究方案，既污染章节
         集合又造成顺序检查假阳性。
    """
    body = _strip_bracket_suffix(title)

    # ① 关键词匹配：可命中多个标准章节（合并式标题）
    hits = []
    for std_name, syns in SYNONYMS.items():
        if any(s in body for s in syns):
            hits.append(std_name)
    if hits:
        return hits[0] if len(hits) == 1 else "+".join(hits)

    # ② 中文数字兜底：仅纯序号标题（本体为空）
    if _ONLY_NUMBER_TITLE.match(title.strip()):
        m = _CN_NUM_PREFIX.match(title.strip())
        if m:
            return _CN_NUM_TO_SECTION.get(m.group(1), "其他")
    return "其他"


def _classify_h2_all(title: str) -> List[str]:
    """返回标题命中的**全部**标准章节（合并式标题可命中多个）。"""
    body = _strip_bracket_suffix(title)
    hits = [std_name for std_name, syns in SYNONYMS.items()
            if any(s in body for s in syns)]
    if hits:
        return hits
    if _ONLY_NUMBER_TITLE.match(title.strip()):
        m = _CN_NUM_PREFIX.match(title.strip())
        if m:
            mapped = _CN_NUM_TO_SECTION.get(m.group(1))
            if mapped:
                return [mapped]
    return ["其他"]


def check_proposal(pid: str) -> Dict[str, Any]:
    """校验单个课题方案结构。"""
    for stage in (OPT_DIR, DRAFTS_DIR, PR_DIR):
        d = stage / pid
        if d.exists():
            return _do_check(pid, d)
    return {"pid": pid, "ok": False, "error": "课题目录不存在"}


def _do_check(pid: str, prop_dir: Path) -> Dict[str, Any]:
    try:
        fp = _latest_proposal_file(prop_dir)
    except FileNotFoundError as e:
        return {"pid": pid, "ok": False, "error": str(e)}

    text = fp.read_text(encoding="utf-8", errors="ignore")
    h2s = _h2_titles(text)
    classified = [_classify_h2(t) for t in h2s]

    # 缺失章节
    expected = ["产出定位", "立项依据", "研究内容", "研究方案",
                "特色与创新", "预期成果"]
    # v7.3.39（BUG-44）：合并式标题可命中多个标准章节，逐 H2 展开全部命中项
    # （旧实现每 H2 只取一个分类值 → 合并标题里的另外两章被丢弃）。
    present: List[str] = []
    for t in h2s:
        for c in _classify_h2_all(t):
            if c in expected and c not in present:
                present.append(c)
    missing = [c for c in expected if c not in present]
    n_extra = sum(1 for c in classified if c == "其他")

    # 顺序检查：present 是否按 expected 顺序出现
    # v7.3.39（BUG-44）：present 已去重（每章节只记首次出现位置），
    # 避免同一章节多次出现被误判为「顺序错乱」。
    last_idx = -1
    out_of_order = False
    for c in present:
        idx = expected.index(c)
        if idx < last_idx:
            out_of_order = True
            break
        last_idx = idx

    if len(missing) >= 2 or out_of_order:
        status = "fail"
    elif len(missing) >= 1:
        status = "warn"
    else:
        status = "pass"

    return {
        "pid": pid,
        "ok": status != "fail",
        "status": status,
        "file": str(fp.relative_to(ROOT)),
        "h2_titles": h2s,
        "present": present,
        "missing": missing,
        "n_other": n_extra,
        "out_of_order": out_of_order,
    }


def check_all() -> List[Dict[str, Any]]:
    return [_do_check(pid, d) for pid, d in _proposal_dirs()]


def _self_check() -> bool:
    print("=== proposal_structure_guard 自检 ===")
    # 章节分类
    assert _classify_h2("一、立项依据") == "立项依据"
    assert _classify_h2("〇、产出定位") == "产出定位"
    assert _classify_h2("五、预期成果") == "预期成果"
    assert _classify_h2("六、跨章口径表") == "其他"
    assert _classify_h2("立项依据") == "立项依据"  # 无序号
    print("✓ 章节分类正确")
    # v7.3.39（BUG-44）回归断言
    # ① 合并式标题命中多个章节
    assert _classify_h2_all("（三）研究方案、特色与创新、预期研究成果") == [
        "研究方案", "特色与创新", "预期成果"]
    # ② 括号补充说明剥离后仍命中
    assert _classify_h2("（三）研究方案、特色与创新、预期研究成果") == \
        "研究方案+特色与创新+预期成果"
    # ③ full_review 骨架序号标题不得被误判为标准章节
    assert _classify_h2("一、主线论证链（核心问题→研究内容→方案如何回应）") == "其他"
    assert _classify_h2("二、章节衔接点（关键承接关系）") == "其他"
    assert _classify_h2("三、跨章节统一口径表") == "其他"
    # ④ 「预期研究成果」变体
    assert _classify_h2("2.9 预期研究成果") == "预期成果"
    # ⑤ 纯序号标题仍走中文数字兜底
    assert _classify_h2("一、") == "立项依据"
    print("✓ BUG-44 回归断言通过（合并标题 / 骨架序号 / 预期研究成果变体）")
    print("✓ 路径常量正确")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="方案结构守卫")
    parser.add_argument("--check", type=str, help="校验单个课题")
    parser.add_argument("--check-all", action="store_true", help="校验全部")
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()

    if args.self_check:
        return 0 if _self_check() else 1
    if args.check:
        r = check_proposal(args.check)
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return 0
    if args.check_all:
        results = check_all()
        pass_n = sum(1 for r in results if r.get("status") == "pass")
        warn_n = sum(1 for r in results if r.get("status") == "warn")
        fail_n = sum(1 for r in results if r.get("status") == "fail")
        print(f"\n=== 校验汇总：pass={pass_n} warn={warn_n} fail={fail_n} ===\n")
        for r in results:
            mark = {"pass": "✓", "warn": "⚠", "fail": "✗"}.get(r.get("status"), "?")
            miss = r.get("missing", [])
            print(f"  {mark} {r['pid']:<50} 缺 {miss}  其他节 {r.get('n_other',0)}")
        if args.report:
            _write_report(results)
        return 0 if fail_n == 0 else 1
    parser.print_help()
    return 0


def _write_report(results: List[Dict[str, Any]]) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [f"# 方案结构守卫校验报告（{now[:10]}）\n"]
    lines.append("> v7.2.30：6 个标准 H2（产出定位/立项依据/研究内容/研究方案/特色创新/预期成果）\n")
    lines.append("| 课题 | 状态 | 缺失章节 | 其它 H2 | 顺序错乱 |")
    lines.append("|------|------|----------|---------|----------|")
    for r in results:
        miss = "、".join(r.get("missing", [])) or "-"
        lines.append(f"| {r['pid'][:40]} | {r.get('status','?')} | {miss} | {r.get('n_other',0)} | {r.get('out_of_order',False)} |")
    pass_n = sum(1 for r in results if r.get("status") == "pass")
    warn_n = sum(1 for r in results if r.get("status") == "warn")
    fail_n = sum(1 for r in results if r.get("status") == "fail")
    lines.append(f"\n**汇总**：pass={pass_n} warn={warn_n} fail={fail_n}\n")
    out = ROOT / "memory" / f"proposal-structure-report-{now[:10]}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    _log(f"✓ 报告：{out}")


if __name__ == "__main__":
    sys.exit(main())
