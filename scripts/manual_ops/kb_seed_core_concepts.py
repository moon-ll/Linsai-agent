#!/usr/bin/env python3
"""核心枢纽概念页补建（v6.10.52 一次性修复，2026-09-25 知识库体检产物）。

背景
----
图谱红链 Top 目标（强场超快×51、MnPS₃×23、altermagnetism×21、
Berry曲率×20、量子几何反演×18）全部因无对应概念页而悬空。这些是
全库高频引用的枢纽概念，值得建立实体页；建页后图谱重建可将数十条
悬空边自动接回。

内容纪律
--------
只写教科书级公认事实，不编造数值；课题特指内容（量子几何反演）
以课题文档口径为准并在正文注明来源。幂等：页面已存在则跳过。

用法
----
    python3 scripts/manual_ops/kb_seed_core_concepts.py [--dry-run]
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

PAGES = [
    {
        "path": "wiki/concepts/强场超快.md",
        "title": "强场超快",
        "tags": ["强场超快", "强场物理", "超快光学"],
        "related": ["高次谐波产生", "三步模型", "CEP门控", "固体高次谐波"],
        "body": (
            "# 强场超快（Strong-Field Ultrafast Science）\n\n"
            "研究激光场强可与原子内场（库仑场）相比拟时物质电子动力学的学科，"
            "时间分辨深入阿秒（10⁻¹⁸ s）量级。核心物理：隧穿/越垒电离、"
            "高次谐波产生（HHG）、阿秒脉冲产生与条纹测量；固体中则包括"
            "强场驱动带间隧穿、动态布洛赫振荡与亚周期电流调控。\n\n"
            "## 与本库的关联\n\n"
            "本库 NSFC-强场超快课题群（BSV 驱动 HHG、固体 HHG、量子几何"
            "反演、MoRiE 强场探针、序参量超快读出等）均以此为伞形领域；"
            "该词在 wiki 引用中出现约 50 次，此前无实体页（2026-09-25 体检"
            "红链 Top1），本页为体检补建枢纽页。\n"
        ),
    },
    {
        "path": "wiki/concepts/交变磁体.md",
        "title": "交变磁体",
        "tags": ["交变磁体", "altermagnet", "磁性材料"],
        "related": ["Berry曲率"],
        "body": (
            "# 交变磁体（Altermagnet）\n\n"
            "继铁磁体、反铁磁体之后被划分出的第三类共线磁性体：宏观磁化"
            "为零（似反铁磁），但因晶体对称性（而非自旋轨道耦合的自旋劈裂）"
            "在 ±k 处产生自旋劈裂能带（似铁磁），由 Šmejkal 等人于 2021-2022 "
            "年系统提出。候选与实证材料包括 MnTe、CrSb 等，按对称性分为 "
            "d 波、g 波等序。物理意义：零杂散场却具备反常霍尔响应、自旋"
            "流与自旋劈裂输运，兼具反铁磁的 THz 快动力学与铁磁的功能性，"
            "是自旋电子学与拓扑物态研究的前沿材料类。\n\n"
            "## 强场超快视角\n\n"
            "HHG 与超快磁光测量正成为探测交变磁性对称性与自旋动力学的新"
            "探针（本库多篇论文笔记涉及 altermagnetic MnTe/CrSb/CoF₃ 的"
            "高次谐波与瞬态磁光研究）。\n"
        ),
    },
    {
        "path": "wiki/concepts/Berry曲率.md",
        "title": "Berry曲率",
        "tags": ["Berry曲率", "拓扑物态", "量子几何"],
        "related": ["量子几何反演", "拓扑绝缘体", "高次谐波产生"],
        "body": (
            "# Berry曲率（Berry Curvature）\n\n"
            "布洛赫能带的几何曲率，表征准动量空间中自旋/能带本征态的"
            "绝热演化几何相位（Berry 相位）的涡旋密度，作用类似动量空间"
            "的等效磁场：产生反常速度与反常霍尔效应，谷体系中支持谷霍尔"
            "输运，并对非线性光学响应（位移电流、非线性霍尔、圆二色性等）"
            "有决定性贡献。布里渊区积分（陈数）给出拓扑分类。\n\n"
            "## 与本库的关联\n\n"
            "量子几何反演课题的核心提取对象之一；此前本词作为引用出现 "
            "20+ 次而无实体页（2026-09-25 体检红链），本页为体检补建。\n"
        ),
    },
    {
        "path": "wiki/concepts/MnPS3.md",
        "title": "MnPS3",
        "tags": ["MnPS3", "二维磁性", "MPX3"],
        "related": ["Berry曲率"],
        "body": (
            "# MnPS₃（三硫磷化锰）\n\n"
            "层状过渡金属磷三硫族化合物 MPX₃ 家族成员：蜂窝格 Mn²⁺ 面"
            "外共线反铁磁半导体，层间以范德华耦合，单层极限仍保持反铁磁"
            "序，是研究本征二维磁性的模型材料体系；可通过插层、应变与"
            "静电调控改变磁序。注意：MnPS₃ 属常规反铁磁体（非交变磁体）。\n\n"
            "## 与本库的关联\n\n"
            "berry-mnps3-rashba 课题的靶向材料（Rashba 型自旋劈裂与 Berry "
            "曲率响应）；本库含多篇 MnPS₃ 超快/第一性原理论文笔记。\n"
        ),
    },
    {
        "path": "wiki/concepts/量子几何反演.md",
        "title": "量子几何反演",
        "tags": ["量子几何", "反问题", "非线性光学"],
        "related": ["Berry曲率", "高次谐波产生"],
        "body": (
            "# 量子几何反演（Quantum Geometry Inversion）\n\n"
            "从可测的非线性光学/输运响应中重构能带量子几何量——Berry 曲率"
            "Ω(k) 与量子度规 g(k)——的反问题方法。候选响应通道：HHG 偏振"
            "谱、非线性霍尔/位移电流、圆偏振响应等。\n\n"
            "## 与本库的关联\n\n"
            "general-quantum-geometry-inversion 课题的核心构想：含 BSV "
            "（亮压缩真空）光场统计对 Ω/g 反演误差与 Fisher 信息的边界"
            "分析（口径见课题设想文档 research_proposals/optimizing/"
            "general-quantum-geometry-inversion-20260726/00_research_idea.md）。"
            "本页为 2026-09-25 体检补建的枢纽页，正文以课题文档为准。\n"
        ),
    },
]


def main(dry_run: bool = False) -> int:
    from kb_wiki import save_wiki_page, get_wiki_page
    from common import now_utc
    from kb_merger import _ensure_wired

    _ensure_wired()
    created, skipped = [], []
    for page in PAGES:
        if get_wiki_page(page["path"]):
            skipped.append(page["path"])
            continue
        meta = {
            "title": page["title"],
            "type": "concepts",
            "created": now_utc(),
            "updated": now_utc(),
            "tags": page["tags"],
            "related": page["related"],
            "source_raw": "",
            "growth_stage": "growing",
            "confidence": 0.7,
        }
        if dry_run:
            created.append(page["path"])
            continue
        save_wiki_page(page["path"], page["body"], meta)
        created.append(page["path"])

    print("枢纽概念页补建: %d 新建, %d 已存在跳过%s"
          % (len(created), len(skipped), "（dry-run）" if dry_run else ""))
    for p in created:
        print("  ✓ %s" % p)
    for p in skipped:
        print("  ○ %s（已存在）" % p)
    return 0


if __name__ == "__main__":
    sys.exit(main(dry_run="--dry-run" in sys.argv))
