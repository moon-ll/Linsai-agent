#!/usr/bin/env python3
"""
params_registry.py — 申请书数值口径表（单一真相源，v7.2.13）

用途：
    根治"跨章数值口径互斥"P0 顽疾（moire 实证：R4-R8 每轮在全部 4 个
    章节复现——核时 10⁸ vs 10⁶、原子数 11,000 vs 12,400、联合维度
    60-100 vs 240-300；writer 局部修复只改点名行，旧值滞留其它章节，
    打地鼠循环致两遍 16 轮 0/5→1/5 模块通过）。

机制（零 LLM，三层）：
    1. 单一真相源：每课题 04_proposal/params.json——key/canonical/
       stale_patterns（旧值正则）/note 四字段
    2. writer 注入：口径表块强制注入 writer prompt（所有会话同一套数）
    3. 事后校验：writer 落盘后 grep 全部章节文件搜 stale_patterns，
       冲突写 05_review/params-conflicts.json 供 critic/monitor 消费

fail-open：params.json 不存在 → 全部 no-op（不影响现有课题）。

用法示例：
    from lifecycle.params_registry import load_params, format_params_block, check_consistency
    params = load_params(prop_dir)
    block = format_params_block(params)
    report = check_consistency(prop_dir, params)

    python3 scripts/lifecycle/params_registry.py --check research_proposals/optimizing/<id>

约束：仅标准库；pathlib；JSON ensure_ascii=False indent=2。
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

if __package__:
    from .constants import JOB_STATUS_DONE  # noqa: F401（占位保持包结构一致）
else:  # 独立运行
    sys.path.insert(0, str(Path(__file__).parent.parent))

from common import now_utc, save_json  # noqa: E402

SECTION_FILES = ["rationale.md", "content.md", "scheme.md",
                 "full_review.md", "references.md"]
# v7.3.27: 方法学手册是衍生文档（03_method/method-manual.md），此前完全
# 不入口径校验——houston r2 实证：params.json 明令禁用的 4.19 eV 在手册
# §0.8/§1.1 两处滞留、1.7×10⁷ CPU·h 与 12–19 万双版本并存，而
# check_consistency 只扫 5 个章节文件 → 返回 0 冲突，writer 既拿不到
# canonical 值也拿不到全册命中位置，只能按 critic 点名的行逐处打补丁。
MANUAL_FILE = Path("03_method") / "method-manual.md"


def params_path(prop_dir: Path) -> Path:
    """口径表路径（每课题一份）。"""
    return prop_dir / "04_proposal" / "params.json"


def load_params(prop_dir: Path) -> Optional[Dict[str, Any]]:
    """加载口径表；不存在返回 None（fail-open 语义：无表=无机制）。"""
    p = params_path(prop_dir)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    entries = data.get("entries", [])
    if not isinstance(entries, list) or not entries:
        return None
    return data


def format_params_block(data: Dict[str, Any]) -> str:
    """渲染 writer/critic prompt 注入块。

    v7.2.19：条目泛化为「数值 + 机制表述」双类——跨章冲突实证不限于
    数值（mos2 r3：同一文献 [13] 在两章两种机制表述互斥、构型"单构型
    vs AA/AB 两构型"互斥），canonical 允许整句规范表述，stale_patterns
    匹配禁用旧表述，机制与数值同表治理。
    """
    lines = [
        "\n【跨章口径表（单一真相源，全章必须一致——含数值与机制表述）】",
        "下表是本申请书的唯一口径。你写入的任何数值或机制/结论表述凡与"
        "下表相关，必须与 canonical 值/表述完全一致；发现所在章节存在"
        "stale 旧值/旧表述时，必须同步修正其出现的所有位置（跨章也要改）。",
        "",
    ]
    for e in data.get("entries", []):
        lines.append(f"- {e.get('key','?')}：{e.get('canonical','?')}"
                     f"{'（' + e['note'] + '）' if e.get('note') else ''}")
        for sp in e.get("stale_patterns", []):
            lines.append(f"  · 禁用旧值/旧表述模式：{sp}")
    lines.append("")
    return "\n".join(lines)


def scan_text_conflicts(text: str, data: Dict[str, Any],
                        label: str = "method-manual") -> List[Dict[str, Any]]:
    """v7.3.27: 零 LLM 扫描任意文本中的 stale_patterns，返回带行号的命中。

    与 check_consistency 的差异：后者按章节文件聚合（section×count），
    本函数按命中点给出行号、命中原文与 canonical，供**写入侧**按小节归并
    动作（一次改净）；不做自动替换（旧值可能出现在"已撤销"等历史表述里，
    机械替换会改坏语义）。
    """
    hits: List[Dict[str, Any]] = []
    if not text:
        return hits
    # 同一位置可能被多个 stale_patterns 命中（如 `4\.19 eV` 与 `4\.19`），
    # 按 (key, 起始偏移) 去重取最长命中，避免注入块重复刷屏
    seen: Dict[tuple, Dict[str, Any]] = {}
    for e in data.get("entries", []):
        for pat in e.get("stale_patterns", []):
            try:
                rx = re.compile(pat)
            except re.error:
                continue
            for m in rx.finditer(text):
                item = {
                    "key": e.get("key", "?"),
                    "stale_pattern": pat,
                    "canonical": e.get("canonical", ""),
                    "section": label,
                    "line": text.count("\n", 0, m.start()) + 1,
                    "found": m.group(0)[:60],
                }
                k = (item["key"], m.start())
                old = seen.get(k)
                if old is None or len(item["found"]) > len(old["found"]):
                    seen[k] = item
    hits = sorted(seen.values(), key=lambda h: h["line"])
    return hits


def scan_manual_conflicts(prop_dir: Path, data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """扫描 03_method/method-manual.md 的口径旧值命中（不存在返回空列表）。"""
    p = prop_dir / MANUAL_FILE
    if not p.exists():
        return []
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    return scan_text_conflicts(text, data)


def format_manual_conflicts_block(hits: List[Dict[str, Any]],
                                  limit: int = 40) -> str:
    """渲染手册写入侧注入块（空命中返回空串）。"""
    if not hits:
        return ""
    lines = [
        "【手册口径旧值命中（零 LLM 扫描，行号=当前手册）】",
        "以下每处都是 params.json 明令禁用的旧值/旧表述，本轮必须改净为 canonical；",
        "同一旧值跨多个小节时按小节归并为动作，禁止只改 critic 点名的行。",
    ]
    for h in hits[:limit]:
        _canon = (h.get("canonical") or "").replace("\n", " ")[:120]
        lines.append(
            f"- L{h['line']}｜{h['key']}｜命中 `{h['found']}` → canonical：{_canon}"
        )
    if len(hits) > limit:
        lines.append(f"- （另有 {len(hits) - limit} 处命中未列出，按同一纪律处理）")
    return "\n".join(lines) + "\n\n"


def check_consistency(prop_dir: Path, data: Dict[str, Any]) -> Dict[str, Any]:
    """零 LLM 事后校验：grep 各章节文件搜 stale_patterns。

    返回 {checked, conflicts: [{key, stale, sections, hits}], clean}。
    """
    sections_dir = prop_dir / "04_proposal" / "sections"
    texts: Dict[str, str] = {}
    for fname in SECTION_FILES:
        f = sections_dir / fname
        if f.exists():
            try:
                texts[fname] = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                texts[fname] = ""
    # v7.2.61: 覆盖面扩展到设想文件——mos2 实证：00_research_idea.md L35
    # 残留被封禁的「单构型…约一个量级」表述整整未被查出（registry 只扫
    # 5 个 section 文件）。设想文件与 sections 一样是口径一致性的守护面。
    idea_file = prop_dir / "00_research_idea.md"
    if idea_file.exists():
        try:
            texts["00_research_idea.md"] = idea_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            texts["00_research_idea.md"] = ""

    conflicts: List[Dict[str, Any]] = []
    checked = 0
    for e in data.get("entries", []):
        for pat in e.get("stale_patterns", []):
            checked += 1
            try:
                rx = re.compile(pat)
            except re.error:
                continue
            hits = []
            for fname, text in texts.items():
                found = rx.findall(text)
                if found:
                    hits.append({"section": fname, "count": len(found)})
            if hits:
                conflicts.append({
                    "key": e.get("key", "?"),
                    "stale_pattern": pat,
                    "canonical": e.get("canonical", ""),
                    "hits": hits,
                })
    return {
        "checked": checked,
        "conflicts": conflicts,
        "clean": not conflicts,
        "checked_at": now_utc(),
    }


def run_check_and_persist(prop_dir: Path, round_num: int = 0) -> Dict[str, Any]:
    """校验并落盘 05_review/params-conflicts.json（供 critic/monitor 读）。"""
    data = load_params(prop_dir)
    if data is None:
        return {"active": False}
    report = check_consistency(prop_dir, data)
    report["active"] = True
    report["round"] = round_num
    try:
        out = prop_dir / "05_review" / "params-conflicts.json"
        save_json(out, report)
    except Exception:
        pass
    return report


def _seed_template() -> Dict[str, Any]:
    """口径表模板（moire R8 critic 实锤的四个冲突作示例字段）。"""
    return {
        "_doc": "数值口径表：key=指标名，canonical=唯一正确值/表述，"
                "stale_patterns=禁用旧值正则（python re 语法），note=口径说明",
        "entries": [
            {
                "key": "TDDFT 全原胞计算成本",
                "canonical": "单次 10⁶ 核时 × 100 参数点扫描 = 总账 10⁸ 核时",
                "stale_patterns": [r"11,?000 原子", r"10⁸核时(?!总账)"],
                "note": "三章统一此折算口径，禁止单章裸写 10⁸ 或 11,000 原子",
            },
            {
                "key": "双层原胞原子数",
                "canonical": "双层 12,400",
                "stale_patterns": [r"11,?000"],
                "note": "6,200 单层 / 12,400 双层",
            },
            {
                "key": "联合观测维度",
                "canonical": "240-300（对有效自由度 6-10 的冗余 24-50×）",
                "stale_patterns": [r"60[–-]100 ?(点|维|个)", r"6[–-]17×"],
                "note": "§3.2.4 与 §3.5/§2.2.2 必须同一维度并复算冗余",
            },
            {
                "key": "SHG 调制实验结论",
                "canonical": "开关比超 10 倍、SHG 抑制约 90%（Shan, Nature 600, 235）",
                "stale_patterns": [r"调制[（(]?[>＞] ?30%"],
                "note": "引文准确性红线：不得夸大为 >30% 调制",
            },
            {
                "key": "机制表述条目示例（v7.2.19 泛化）",
                "canonical": "层间堆叠对称性决定偶阶相消与逐层相干累积（I∝n²）",
                "stale_patterns": [r"层间几何相位(?!累积)"],
                "note": "canonical 允许整句规范表述：同一机制在所有章节必须同表述，"
                        "禁止同一文献在各章各说各话（mos2 [13] 实证）",
            },
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="数值口径表（单一真相源）")
    parser.add_argument("--check", metavar="PROP_DIR", help="校验课题口径一致性")
    parser.add_argument("--show", metavar="PROP_DIR", help="显示口径表")
    parser.add_argument("--seed", metavar="PROP_DIR", help="写入模板口径表（幂等：已存在跳过）")
    args = parser.parse_args()

    if args.show:
        data = load_params(Path(args.show))
        print(json.dumps(data, ensure_ascii=False, indent=2) if data else "（无口径表）")
        return 0
    if args.check:
        prop_dir = Path(args.check)
        data = load_params(prop_dir)
        if data is None:
            print("○ 无口径表（机制未启用）")
            return 0
        r = check_consistency(prop_dir, data)
        print(f"校验 {r['checked']} 个旧值模式，冲突 {len(r['conflicts'])} 个")
        for c in r["conflicts"]:
            secs = ", ".join(f"{h['section']}×{h['count']}" for h in c["hits"])
            print(f"  ✗ {c['key']}: {c['stale_pattern']} @ {secs}")
        return 0 if r["clean"] else 1
    if args.seed:
        prop_dir = Path(args.seed)
        p = params_path(prop_dir)
        if p.exists():
            print("○ 已存在，跳过")
            return 0
        save_json(p, _seed_template())
        print(f"✓ 模板口径表 → {p}")
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
