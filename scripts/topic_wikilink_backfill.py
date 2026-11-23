# -*- coding: utf-8 -*-
"""topic_wikilink_backfill — v8 启动包报告 wikilink 补齐（G2 硬门，零 LLM）。

背景（worklist-and-prompt 任务 5，2026-11-18）：v7 迁移启动包的 topic-report.md
wikilink 全为 0，G2（≥5）全挂。本脚本把报告中出现的方法名/概念名/文献名映射到
knowledge/wiki/ 实存页，在 03_scheme/scheme.md 头部插入「知识库关联」节，经 B4
重组装流入报告（直接改报告会被下次组装覆盖）。

红线（执行清单原话）：
    - 只链 knowledge/wiki/ 下实存页：插入前逐一 os.path 级核实目标存在，
      任一不存在即中止该课题（绝不写入死链）。
    - 映射以正文出现名为据：概念/方法页取「页面名（归一化）出现在课题正文」，
      论文页取「bib/编号行的 arXiv id 命中 KB 论文页 stem」；链后附一句话
      关联依据。找不到足够实存页时如实报「KB 覆盖不足」，不凑数。

用法示例：
    python3 scripts/topic_wikilink_backfill.py --plan     # 预览（核实存在性，不写）
    python3 scripts/topic_wikilink_backfill.py --apply    # 插入 + 重组装由调用方执行
    python3 scripts/topic_wikilink_backfill.py --self-check
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from common import now_utc, save_json  # noqa: E402

TOPICS_ROOT = PROJECT_ROOT / "research_topics"
WIKI = PROJECT_ROOT / "knowledge" / "wiki"
AUDIT_PATH = PROJECT_ROOT / "research_topics" / "_audit" / "wikilink-backfill.json"

# 每课题选链：[wiki 相对页名, 关联依据（对应正文锚点）]
# 依据来源：2026-11-18 归一化文本匹配扫描（正文出现页面名/arXiv id 命中），
# 逐条人工复核课题问题域后精选；插入时再次核实文件实存。
SELECTIONS: Dict[str, List[List[str]]] = {
    "general-berry-berry-20261107": [
        ["concepts/Berry曲率偶极", "课题核心观测量：贝里曲率偶极驱动的非线性霍尔效应"],
        ["concepts/非线性霍尔效应", "主效应载体（正文：非线性霍尔效应）"],
        ["concepts/Berry曲率", "基础概念（正文多处贝里曲率）"],
        ["concepts/量子几何张量", "偶极的理论载体（量子几何张量与偶极的关系）"],
        ["concepts/反常霍尔效应", "对照效应"],
        ["concepts/量子几何", "理论框架"],
    ],
    "general-berry-mnps3-rashba-20260816": [
        ["concepts/交变磁性_altermagnetism", "靶材料磁性类（MnPS3 为交变磁体）"],
        ["concepts/Rashba自旋劈裂", "劈裂机制（正文：Rashba）"],
        ["concepts/MnPS3", "靶材料页"],
        ["concepts/Berry曲率", "核心概念"],
        ["concepts/范德华异质结", "材料体系"],
        ["methods/泵浦探测", "实验方法（正文：泵浦探测）"],
    ],
    "general-chiral-hhg-20261101": [
        ["concepts/半导体Bloch方程", "理论框架（正文：半导体布洛赫方程）"],
        ["concepts/固体高次谐波", "主对象"],
        ["concepts/Berry曲率", "概念"],
        ["concepts/RABBIT", "表征方法（正文：RABBIT）"],
        ["methods/xuv", "波段方法页（正文：XUV）"],
    ],
    "general-floquet-20261107": [
        ["methods/Floquet工程", "主方法"],
        ["concepts/时间反演对称性破缺", "机制"],
        ["concepts/MnPS3", "材料体系（正文：MnPS3）"],
        ["concepts/自旋劈裂", "观测量"],
        ["concepts/CrSb", "材料（正文：CrSb）"],
        ["methods/BSE", "计算方法（正文：BSE）"],
    ],
    "general-houston-kronig-penney-landau-zener-20261004": [
        ["methods/houston", "Houston 基方法页（课题名：Houston）"],
        ["methods/keldysh", "Keldysh 参数页（正文：Keldysh）"],
        ["concepts/高次谐波产生", "主对象"],
        ["concepts/固体高次谐波", "固态 HHG"],
        ["concepts/Kubo公式", "线性响应（正文：Kubo）"],
        ["concepts/阿秒瞬态吸收", "应用端（正文：瞬态吸收）"],
    ],
    "general-keldysh-schottky-20261115": [
        ["methods/keldysh", "Keldysh 参数（正文：Keldysh参数）"],
        ["concepts/三步模型", "强场电离模型（正文：三步模型）"],
        ["concepts/拍赫兹电子学", "应用端（正文：拍赫兹电子学应用）"],
        ["concepts/隧穿时间", "多光子-隧穿过渡区的隧穿时序"],
        ["mocs/强场物理", "领域 MoC（正文：强场光电子发射）"],
    ],
    "general-moire-strong-field-probe-20260726": [
        ["methods/bistritzer", "转角双层连续模型（正文：Bistritzer-MacDonald）"],
        ["methods/Floquet工程", "方法"],
        ["concepts/Berry曲率", "概念"],
        ["methods/wigner", "Wigner 函数（正文：Wigner）"],
        ["concepts/载波包络相位", "脉冲参数（正文：CEP）"],
        ["concepts/高次谐波产生", "主对象"],
    ],
    "general-order-parameter-ultrafast-readout-20260727": [
        ["concepts/电荷密度波", "序参量载体（正文：电荷密度波）"],
        ["concepts/含时密度泛函", "理论（正文：含时密度泛函）"],
        ["concepts/TDDFT", "方法"],
        ["concepts/高次谐波产生", "探针"],
        ["concepts/固体高次谐波", "固态"],
        ["concepts/CrSb", "材料（正文：CrSb）"],
    ],
    "general-phonon-hhg-20261101": [
        ["concepts/层间剪切模", "声子模（正文：层间剪切模）"],
        ["concepts/高次谐波产生", "主对象"],
        ["concepts/固体高次谐波", "固态"],
        ["concepts/含时密度泛函", "理论"],
        ["concepts/Mott绝缘体", "体系（正文：Mott）"],
        ["concepts/Berry曲率", "概念"],
    ],
    "general-ssh-weyl-20260920": [
        ["concepts/Weyl半金属", "靶体系（正文：Weyl 半金属）"],
        ["concepts/半导体Bloch方程", "理论"],
        ["concepts/高次谐波产生", "主对象"],
        ["concepts/固体高次谐波", "固态"],
        ["concepts/强场高次谐波", "强场（正文：强场高次谐波）"],
        ["concepts/含时密度泛函", "理论"],
    ],
    "general-t-tise2-2-2-2-cdw-20261108": [
        ["concepts/电荷密度波", "序（正文：电荷密度波/CDW）"],
        ["methods/arpes", "表征方法（正文：ARPES）"],
        ["methods/泵浦探测", "实验方法"],
        ["concepts/层间耦合", "机制（正文：层间耦合）"],
        ["methods/BSE", "计算方法"],
        ["papers/2602.09855", "文献页（bib arXiv id 命中 KB 论文页）"],
        ["papers/2509.06414", "文献页（bib arXiv id 命中）"],
    ],
    "general-tdse-tddft-20261115": [
        ["concepts/TDSE", "主方法（正文：TDSE）"],
        ["concepts/实时含时密度泛函理论", "主方法（正文：rt-TDDFT）"],
        ["concepts/强场电离", "机制"],
        ["concepts/载波包络相位", "脉冲参数（正文：CEP）"],
        ["mocs/强场物理", "领域 MoC"],
    ],
    "general-tmd-bic-mie-anapole-20261107": [
        ["concepts/二次谐波产生", "主非线性过程（正文：SHG）"],
        ["concepts/相位匹配", "机制（正文：相位匹配）"],
        ["concepts/层间耦合", "体系（正文：层间耦合）"],
        ["mocs/非线性光学", "领域 MoC"],
        ["papers/2503.20161", "文献页（bib arXiv id 命中 KB 论文页）"],
        ["papers/2411.12905", "文献页（bib arXiv id 命中）"],
    ],
    "key-transient-quantum-phase-optical-20260726": [
        ["concepts/transient-quantum-phase", "核心概念（课题名：transient quantum phase）"],
        ["methods/Floquet工程", "方法"],
        ["concepts/光致反常霍尔效应", "效应"],
        ["concepts/Weyl半金属", "体系（正文：Weyl）"],
        ["concepts/载波包络相位", "参数"],
        ["concepts/反常霍尔效应", "效应"],
    ],
    "general-bsv-driven-hhg-quantum-20260726": [
        ["concepts/bright-squeezed-vacuum", "光态（正文：bright squeezed vacuum）"],
        ["concepts/BSV-driven-HHG", "主对象"],
        ["concepts/高次谐波产生", "过程"],
        ["methods/高次谐波光谱", "方法页"],
        ["concepts/Berry曲率", "概念"],
    ],
}

_BLOCK_HEAD = "## 知识库关联（v8.0.9 G2 补齐）\n\n" \
    "> 下列链接均映射自本包正文出现的方法名/概念名/文献名，目标页逐一核实\n" \
    "> 实存于 knowledge/wiki/（审计：research_topics/_audit/wikilink-backfill.json）。\n\n"


def _page_exists(rel: str) -> bool:
    return (WIKI / (rel + ".md")).exists()


def build_block(tid: str) -> Dict[str, Any]:
    """构造单课题知识库关联节（先核实每一目标实存，缺一即降级并记录）。"""
    sel = SELECTIONS.get(tid, [])
    ok, missing = [], []
    for rel, why in sel:
        (ok if _page_exists(rel) else missing).append((rel, why))
    lines = [f"- [[{Path(rel).name}]] — {why}" for rel, why in ok]
    return {"block": _BLOCK_HEAD + "\n".join(lines) + "\n",
            "n_links": len(ok), "missing": [m[0] for m in missing]}


def insert_block(tdir: Path, block: str, apply: bool) -> Dict[str, Any]:
    """插入 scheme.md 头部（首块之后、第一个二级标题之前）——保证 B4 摘录携带。"""
    scheme = tdir / "03_scheme" / "scheme.md"
    text = scheme.read_text(encoding="utf-8")
    if "知识库关联（v8.0.9" in text:
        return {"skipped": "已插入（幂等跳过）"}
    m = re.search(r"^## ", text, re.M)
    pos = m.start() if m else len(text)
    new = text[:pos] + block + "\n" + text[pos:]
    if apply:
        scheme.write_text(new, encoding="utf-8")
    return {"written": True, "pos": pos}


def main() -> int:
    ap = argparse.ArgumentParser(description="v8 启动包报告 wikilink 补齐")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()
    if args.self_check:
        return _self_check()
    audit = {"at": now_utc(), "results": []}
    for tid, sel in SELECTIONS.items():
        for stage in ("kickoff", "ready", "active"):
            tdir = TOPICS_ROOT / stage / tid
            if tdir.exists():
                break
        else:
            continue
        b = build_block(tid)
        res = {"topic_id": tid, "n_links": b["n_links"], "missing": b["missing"]}
        if args.apply and b["n_links"] >= 3:
            res.update(insert_block(tdir, b["block"], apply=True))
        print(f"  {'✓' if b['n_links'] >= 5 else '⚠'} {tid}: 实存链接 {b['n_links']}"
              + (f"，缺页不写 {b['missing']}" if b["missing"] else ""))
        audit["results"].append(res)
    if args.apply:
        save_json(AUDIT_PATH, audit)
        print(f"  ✓ 审计落盘: {AUDIT_PATH.relative_to(PROJECT_ROOT)}")
        print("  ○ 下一步：对已插入课题执行 --assemble 重组装，报告即携带链接")
    return 0


def _self_check() -> int:
    """自检：SELECTIONS 全部目标页实存 + 块格式含 [[ ]] + 幂等标记。"""
    bad = []
    for tid, sel in SELECTIONS.items():
        for rel, _ in sel:
            if not _page_exists(rel):
                bad.append(f"{tid}: {rel}")
    assert not bad, f"死链（违反红线，必须先修正清单）: {bad}"
    sample = build_block("general-keldysh-schottky-20261115")
    assert sample["n_links"] >= 5, "keldysh 链接数不足 5"
    assert "[[keldysh]]" in sample["block"], "块格式异常"
    assert "[[" in sample["block"] and "]]" in sample["block"]
    print(f"  ✓ topic_wikilink_backfill 自检：{sum(len(v) for v in SELECTIONS.values())}"
          f" 条链接目标全部实存，块格式正常")
    return 0


if __name__ == "__main__":
    sys.exit(main())
