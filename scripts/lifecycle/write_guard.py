#!/usr/bin/env python3
"""写作并发守卫（零 LLM，供 lifecycle 派活/落盘钩子调用）。

用途：
1. 派活前检查提案目录下的 `.write-lock`——锁存在且持有者不是该 job 时跳过并记录；
2. writer 落盘后登记写入日志，同一章节 10 分钟内出现 ≥2 个不同 writer 即判定冲突；
3. writer 落盘后复核历史 round-N 评审报告的版本存证哈希，不一致即把报告改名
   `*.stale-<时间戳>.md`（保留原文件，不静默覆盖）。

用法示例：
    python3 scripts/lifecycle/write_guard.py --self-check
    python3 scripts/lifecycle/write_guard.py --prop-dir research_proposals/optimizing/xxx --section content

约定：
- 所有函数 fail-open：异常由调用方捕获后继续主流程；
- 不写正文，只读正文哈希、改名旧报告、写 `05_review/.write-guard/` 下的审计文件。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent.parent

# v7.3.52（BUG-47b）：方法手册是第六评审模块，产物路径与申请书正文 5 模块
# 不同（03_method/method-manual.md，非 04_proposal/sections/）。
# 常量取自 proposal_sections.py（唯一真相源，无循环导入——该模块零 import）。
try:
    from proposal_sections import MANUAL_SECTION_KEY
except Exception:  # pragma: no cover - 导入失败时退化为字面量，fail-open
    MANUAL_SECTION_KEY = "method_manual"

LOCK_NAME = ".write-lock"
JOURNAL_DIR = ".write-guard"
CONFLICT_WINDOW_S = 600

# 报告头存证写法（round-3 / round-4 / 首轮 round-3-provenance）
_HASH_PATTERNS = [
    re.compile(r"评前 sha256：`([0-9a-f]{64})`"),
    re.compile(r"评前 sha256:\s*`?([0-9a-f]{64})`?"),
    re.compile(r"被评文件 sha256：`([0-9a-f]{64})`"),
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _sections_dir(prop_dir: Path) -> Path:
    return prop_dir / "04_proposal" / "sections"


def _section_file(prop_dir: Path, section_key: str) -> Path:
    """章节正文落盘路径。

    v7.3.52 BUG-47b 修复：`method_manual` 的产物不在 `04_proposal/sections/`
    （第六评审模块，手册是衍生文档，唯一真相源 `03_method/method-manual.md`，
    见 proposal_sections.py:57 边界声明）。旧实现对所有 section_key 一律
    拼 `sections/{key}.md`，对 method_manual 恒指向不存在的路径 →
    `mark_stale_reports` 恒返回 checked=0（静默失效），且
    `record_section_write` 记录到空 sha256。

    生产实证：houston 的 writes.jsonl 里 method_manual 的 sha256 恒为
    空串（2026-11-06T08:03:18 那条），其余章节均为 64 位哈希。
    """
    if section_key == MANUAL_SECTION_KEY:
        return prop_dir / "03_method" / "method-manual.md"
    return _sections_dir(prop_dir) / f"{section_key}.md"


def _report_round(report_name: str) -> Optional[int]:
    """从报告文件名解析轮次号。

    v7.3.52（BUG-47a）：只认**严格匹配**「critic-round-{n}-{section}.md」
    的文件——`critic-round-3-content-postfix.md` /
    `critic-round-3-content.pre-l101.md` / `critic-round-3-content.md.bak`
    等派生文件不是轮次报告，不参与陈旧判定（派生文件通常无存证哈希，
    旧实现实际也未命中，此处显式化以免误判轮次）。

    返回 None 表示文件名不含可解析轮次（调用方按「非轮次报告」处理）。
    """
    m = re.match(r"^critic-round-(\d+)-", report_name)
    if not m:
        return None
    return int(m.group(1))


def _review_dir(prop_dir: Path) -> Path:
    return prop_dir / "05_review"


def _guard_dir(prop_dir: Path) -> Path:
    d = _review_dir(prop_dir) / JOURNAL_DIR
    d.mkdir(parents=True, exist_ok=True)
    return d


def _append_jsonl(path: Path, record: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_write_lock(prop_dir: Path) -> Optional[Dict[str, str]]:
    """解析 `.write-lock`：返回 {holder, frozen_at, raw}；无锁返回 None。"""
    lock = prop_dir / LOCK_NAME
    if not lock.exists():
        return None
    raw = lock.read_text(encoding="utf-8", errors="replace")
    holder = ""
    m = re.search(r"持有者[：:]\s*(.+)", raw)
    if m:
        holder = m.group(1).strip()
    m2 = re.search(r"冻结时间[：:]\s*(.+)", raw)
    return {
        "holder": holder,
        "frozen_at": m2.group(1).strip() if m2 else "",
        "raw": raw,
    }


def check_write_lock(prop_dir: Path, job_holder: str) -> Tuple[bool, str]:
    """派活前守卫：锁存在且持有者不是本 job → (False, 原因)。"""
    info = read_write_lock(prop_dir)
    if info is None:
        return True, "无写锁"
    holder = info.get("holder", "")
    if job_holder and holder and job_holder in holder:
        return True, f"写锁由本 job 持有（{holder}）"
    shown = holder or "未注明"
    return False, f"写锁存在且持有者为「{shown}」，非 {job_holder}"


def record_section_write(prop_dir: Path, section_key: str, job_holder: str,
                         lock_held_by_caller: bool = False) -> Dict[str, Any]:
    """登记一次 writer 落盘；同一章节 10 分钟内 ≥2 个不同写入者 → conflict=True。"""
    section_path = _section_file(prop_dir, section_key)
    sha = _sha256(section_path) if section_path.exists() else ""
    now = time.time()
    journal_path = _guard_dir(prop_dir) / "writes.jsonl"
    record = {
        "ts": _now_iso(),
        "epoch": round(now, 3),
        "section": section_key,
        "holder": job_holder,
        "sha256": sha,
        "lock_held_by_caller": bool(lock_held_by_caller),
    }
    _append_jsonl(journal_path, record)

    recent: List[Dict[str, Any]] = []
    if journal_path.exists():
        for line in journal_path.read_text(encoding="utf-8").splitlines():
            try:
                item = json.loads(line)
            except Exception:
                continue
            if item.get("section") != section_key:
                continue
            if now - float(item.get("epoch", 0)) <= CONFLICT_WINDOW_S:
                recent.append(item)

    holders = {i.get("holder", "") for i in recent if i.get("holder")}
    conflict = len(holders) >= 2
    if conflict:
        reason = (
            f"同一章节 {section_key} 在 {CONFLICT_WINDOW_S}s 内出现 {len(holders)} 个 "
            f"写入者：{', '.join(sorted(holders))}"
        )
        _append_jsonl(
            _guard_dir(prop_dir) / "conflicts.jsonl",
            {"ts": _now_iso(), "section": section_key, "holders": sorted(holders),
             "reason": reason},
        )
        return {"sha256": sha, "conflict": True, "reason": reason,
                "recent_writers": len(holders)}
    return {"sha256": sha, "conflict": False, "reason": "", "recent_writers": len(holders)}


def _report_hashes(report_path: Path) -> List[str]:
    try:
        text = report_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    found: List[str] = []
    for pat in _HASH_PATTERNS:
        for m in pat.finditer(text):
            if m.group(1) not in found:
                found.append(m.group(1))
    return found


def mark_stale_reports(prop_dir: Path, section_key: str,
                       current_sha: Optional[str] = None,
                       current_round: Optional[int] = None) -> Dict[str, Any]:
    """复核 critic-round-* 报告存证哈希；不一致则改名 stale（不删除、不覆盖）。

    v7.3.50 BUG-47 修复——「同轮报告误伤」：writer 落盘后正文哈希必然与
    **本轮 critic 报告的存证哈希不同**（writer 的职责就是改正文）。旧实现
    不区分轮次，凡存证哈希与当前正文不符即改名 stale → 本轮刚产出、正被
    下一步 critic/写后复检消费的 `critic-round-N-{section}.md` 会被当场改名，
    而 `executor._read_critic_report` 按精确名 `critic-round-{n}-{section}.md`
    读盘 → 读到空 → `score=0.0 / dim_scores={}` → 该章节后续质量门全部失真。

    修复口径（不改判据措辞，只改作用范围）：
    1. `current_round` 传入时，**跳过本轮报告**（本轮报告的哈希本来就该
       与「改后正文」不同）；只对**历史轮次**（round < current_round）的报告
       做陈旧判定——那才是「旧报告描述的版本已被后续改动覆盖」的真场景。
    2. `current_round` 未传入时保持旧行为（全量比对），仅供 CLI 手工查询。

    实测（chiral，round-5 同版本复评）：修复前 writer 落盘即把
    `critic-round-5-content.md` 与 `critic-round-3-content.md` 一并改名；
    修复后仅 `critic-round-3-content.md` 被改名，本轮报告保持原名可被读盘。
    """
    section_path = _section_file(prop_dir, section_key)
    if not section_path.exists():
        return {"checked": 0, "stale": []}
    cur = current_sha or _sha256(section_path)
    review = _review_dir(prop_dir)
    stale: List[str] = []
    checked = 0
    skipped_current_round: List[str] = []
    for rp in sorted(review.glob(f"critic-round-*-{section_key}.md")):
        # 只处理严格匹配「critic-round-{n}-{section}.md」的报告；postfix /
        # pre-l101 / .bak / .stale 等派生文件不在判定范围内（旧实现同样
        # 用同一 glob，但派生文件通常无存证哈希故实际未命中，此处显式化）。
        hashes = _report_hashes(rp)
        if not hashes:
            continue
        # v7.3.52（BUG-47a）：本轮报告豁免——writer 落盘后正文哈希必然与
        # 本轮 critic 报告的存证哈希不同（writer 的职责就是改正文），
        # 若一并改名则 executor._read_critic_report 按精确名
        # `critic-round-{n}-{section}.md` 读盘会读到空 → score=0.0 /
        # dim_scores={} → 该章节后续质量门全部失真。只对历史轮次
        # （round < current_round）的报告做陈旧判定。
        rp_round = _report_round(rp.name)
        if current_round is not None and rp_round is not None and rp_round >= current_round:
            skipped_current_round.append(rp.name)
            continue
        checked += 1
        # 报告存证里可能同时有评前/评后两枚哈希，任一与当前一致即视为同一版本
        if cur in hashes:
            continue
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        target = rp.with_name(f"{rp.stem}.stale-{ts}.md")
        rp.rename(target)
        stale.append(target.name)
        _append_jsonl(
            _guard_dir(prop_dir) / "stale-reports.jsonl",
            {"ts": _now_iso(), "section": section_key,
             "report": rp.name, "renamed_to": target.name,
             "report_sha256": hashes, "current_sha256": cur},
        )
    return {"checked": checked, "stale": stale,
            "skipped_current_round": skipped_current_round}


def _self_check() -> bool:
    import tempfile
    ok = True
    with tempfile.TemporaryDirectory() as td:
        prop = Path(td) / "prop"
        (prop / "04_proposal" / "sections").mkdir(parents=True)
        (prop / "05_review").mkdir(parents=True)
        section = prop / "04_proposal" / "sections" / "content.md"
        section.write_text("正文 A", encoding="utf-8")
        ok &= check_write_lock(prop, "job:j1")[0]

        (prop / LOCK_NAME).write_text("- 持有者：TraeCode 会话\n", encoding="utf-8")
        ok &= check_write_lock(prop, "job:j1")[0] is False
        ok &= check_write_lock(prop, "job:j1")[1].startswith("写锁存在")
        ok &= check_write_lock(prop, "TraeCode 会话")[0]

        sha1 = _sha256(section)
        (prop / LOCK_NAME).unlink()
        r1 = record_section_write(prop, "content", "job:j1")
        ok &= r1["conflict"] is False
        r2 = record_section_write(prop, "content", "job:j2")
        ok &= r2["conflict"] is True

        report = prop / "05_review" / "critic-round-4-content.md"
        report.write_text(
            "<!-- round-4-sha256 -->\n- 评前 sha256：`" + sha1 + "`\n", encoding="utf-8")
        res = mark_stale_reports(prop, "content")
        ok &= res["stale"] == []
        section.write_text("正文 B", encoding="utf-8")
        res2 = mark_stale_reports(prop, "content")
        ok &= len(res2["stale"]) == 1
        ok &= (not report.exists()) and (prop / "05_review" / res2["stale"][0]).exists()
    print("✓ write_guard self-check passed" if ok else "✗ write_guard self-check failed")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description="写作并发守卫（自检/只读查询）")
    ap.add_argument("--self-check", action="store_true", help="运行内置自检")
    ap.add_argument("--prop-dir", help="提案目录（只读查询）")
    ap.add_argument("--section", help="章节键，如 content")
    args = ap.parse_args()
    if args.self_check:
        return 0 if _self_check() else 1
    if args.prop_dir:
        prop = Path(args.prop_dir)
        if not prop.is_absolute():
            prop = PROJECT_ROOT / prop
        info = read_write_lock(prop)
        print(json.dumps({"write_lock": info and {k: info[k] for k in ("holder", "frozen_at")}},
                         ensure_ascii=False, indent=2))
        if args.section:
            print(json.dumps(mark_stale_reports(prop, args.section), ensure_ascii=False, indent=2))
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
