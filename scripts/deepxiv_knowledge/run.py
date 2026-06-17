#!/usr/bin/env python3
"""
run.py — deepxiv 论文获取流水线
v5: 使用 --head (JSON) 作为主要数据源，--preview 补充结构化内容
"""

import sys, time
from pathlib import Path

_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

try:  # 包模式优先，脚本模式回退
    from .fetch_core import fetch_head, fetch_preview, _extract_sections_from_head, _extract_sections_from_preview
    from .checkpoint import Checkpoint
    from .paper_writer import write_paper
except ImportError:
    from fetch_core import fetch_head, fetch_preview, _extract_sections_from_head, _extract_sections_from_preview
    from checkpoint import Checkpoint
    from paper_writer import write_paper

PROJECT_ROOT = Path(__file__).parent.parent.parent
OUT_DIR = PROJECT_ROOT / "knowledge" / "raw" / "papers"
CKPT_PATH = PROJECT_ROOT / "knowledge" / "raw" / "checkpoint.json"

# ============================================================
# 调研论文主列表（deepxiv search 筛选，2010-2026，HHG 光谱学）
# ============================================================

MASTER_LIST = [
    # --- 原子 HHG 理论与测量（8 篇，priority 1）---
    ("1012.3863",  ["theory", "measurement", "RABBITT", "attosecond"], 1),
    ("1102.1461",  ["theory", "measurement", "streaking", "TDSE"], 1),
    ("physics/9906053", ["theory", "three-step", "quantum-model"], 2),
    ("0707.4192", ["theory", "Lewenstein-model", "SFA"], 2),
    ("1812.11447", ["theory", "SFA", "strong-field-approximation"], 2),
    ("1910.13791", ["theory", "quantum-optics", "HHG"], 2),
    ("1809.08109", ["theory", "reciprocal-space", "trajectory"], 2),
    ("1006.3942", ["theory", "water-window", "phase-matching"], 1),
    # --- 测量方法（9 篇）---
    ("1010.4558",  ["measurement", "transient-absorption", "helium"], 1),
    ("1401.2878",  ["measurement", "streaking", "time-delay"], 2),
    ("1010.2800",  ["measurement", "photoionization", "delay"], 1),
    ("1302.4495",  ["measurement", "noble-gas", "Wigner-delay"], 2),
    ("1707.05445", ["measurement", "angular-streaking", "tunnelling"], 1),
    ("0908.2575",  ["measurement", "VMI", "tomography"], 2),
    ("1411.0838",  ["measurement", "COLTRIMS", "reaction-microscope"], 2),
    ("1005.1253",  ["measurement", "covariance", "correlation"], 2),
    ("1301.0771",  ["measurement", "transient-absorption", "quantum-interference"], 2),
    # --- 固体 HHG（9 篇）---
    ("1502.07183", ["solids", "Bloch-electrons", "TDSE"], 1),
    ("1609.09852", ["solids", "multi-level", "HHG-model"], 1),
    # 1708.02658 → 已回收（arXiv ID 漂移，指向无关数学论文）
    # ("1708.02658", ["solids", "electron-dynamics", "attosecond"], 1),
    ("1806.11232", ["solids", "topological", "sub-cycle"], 1),
    ("1710.02208", ["solids", "water-window", "attosecond-streaking"], 2),
    ("1807.02961", ["solids", "2D-materials", "hexagonal-boron-nitride"], 2),
    ("2008.03619", ["solids", "metasurface", "even-odd-HHG"], 2),
    ("1812.09339", ["solids", "nanostructure", "plasmon"], 2),
    ("1906.10224", ["solids", "spin-polarised", "defects"], 2),
    # --- 分子 HHG（5 篇）---
    ("0712.3710",  ["molecules", "orbital-tomography"], 2),
    ("2103.16228", ["molecules", "self-probing", "HHG-spectroscopy"], 1),
    ("1801.06691", ["molecules", "tomography", "asymmetric-orbital"], 2),
    ("1412.1300",  ["molecules", "spectroscopy", "polyatomic"], 2),
    # 1604.06354 → 已回收（arXiv ID 漂移，指向 QED 论文）
    # ("1604.06354", ["molecules", "orbital-symmetry", "reconstruction"], 2),
    # --- 水窗光源（5 篇）---
    ("1207.4653",  ["source", "water-window", "carbon-K-edge"], 1),
    ("1411.1964",  ["source", "spatio-temporal", "soft-X-ray"], 1),
    ("2003.06755", ["source", "water-window", "energy-scaling"], 2),
    ("2101.10547", ["source", "water-window", "mid-IR"], 2),
    ("2012.08856", ["source", "nanowire", "water-window"], 2),
    # --- 综述与路线图（3 篇）---
    ("1201.5094",  ["review", "frontiers", "atomic-HHG"], 1),
    ("2604.15085", ["review", "roadmap", "attosecond-science"], 1),
    ("2501.06752", ["review", "ultrafast-dynamics", "theoretical"], 2),
    # --- 其他重要进展（5 篇）---
    # 1810.06673 → 已回收（arXiv ID 漂移，指向 NLP 论文）
    # ("1810.06673", ["solids", "lightwave-electronics"], 2),
    ("2403.19535", ["source", "keV", "high-flux"], 2),
    ("2306.16212", ["measurement", "all-attosecond", "pump-probe"], 2),
    ("2512.09585", ["measurement", "all-attosecond", "transient-absorption"], 2),
    ("2304.12547", ["solids", "particle-wave", "perspective"], 2),
    # === 扩展调研：实验方法（脉冲表征 + 相位匹配）===
    ("0707.4228", ["measurement", "attosecond", "FROG", "RABBITT", "characterization"], 1),
    ("1312.1679", ["measurement", "attosecond", "characterization", "isolated-pulse"], 1),
    ("1104.5086", ["measurement", "attosecond", "phase-retrieval", "characterization"], 1),
    ("1602.08144", ["measurement", "attosecond", "characterization", "Rydberg"], 2),
    ("1612.08528", ["measurement", "phase-matching", "nanometer-scale"], 1),
    ("2404.01325", ["measurement", "phase-matching", "X-ray"], 1),
    ("1612.04100", ["measurement", "quasi-phase-matching", "temporal-model"], 2),
    ("2503.08052", ["measurement", "phase-matching", "twisted-solids"], 2),
    # === 扩展调研：光谱学原理（HHG 光谱学 + 量子路径 + 轨道断层成像）===
    ("1009.2224", ["spectroscopy", "HHG-spectroscopy", "aligned-molecules", "near-threshold"], 1),
    ("1211.0917", ["spectroscopy", "HHG-spectroscopy", "transient-grating", "NO2"], 1),
    ("1805.10453", ["spectroscopy", "HHG-spectroscopy", "polarization-state", "solids"], 1),
    ("2003.10430", ["spectroscopy", "HHG-spectroscopy", "solid-state", "dynamics"], 1),
    ("2203.10253", ["spectroscopy", "HHG-spectroscopy", "2D-materials"], 1),
    ("2307.14693", ["spectroscopy", "HHG-spectroscopy", "excitons", "solids"], 2),
    ("1210.4814", ["spectroscopy", "quantum-path", "interference", "molecular-dynamics"], 1),
    ("1502.07422", ["spectroscopy", "quantum-path", "spatiotemporal", "features"], 2),
    ("1401.4050", ["spectroscopy", "orbital-tomography", "plane-wave", "beyond"], 2),
    ("1808.04690", ["spectroscopy", "orbital-tomography", "algorithms", "image-formation"], 2),
    ("1607.00747", ["spectroscopy", "recombination", "electron-hole", "quartz"], 2),
    ("2111.08669", ["spectroscopy", "theory", "solids", "tutorial", "review"], 2),
]


def fetch_one(arxiv_id: str, tags: list, cp: Checkpoint) -> dict:
    """
    获取单篇论文：head (JSON) + section metadata → preview 降级 → 写入。
    优先使用 deepxiv 官方 section 解析（--head），降级到 preview 提取。
    """
    status = cp.get_status(arxiv_id)
    if status in ("verified", "failed"):
        print(f"  ⏭  跳过 {arxiv_id}（{status}）")
        return {"arxiv_id": arxiv_id, "status": status}

    print(f"  → 获取 {arxiv_id} ...", flush=True)

    # Step 1: --head（JSON 元数据 + 官方 section 摘要）
    data = fetch_head(arxiv_id)
    if not data:
        cp.set_status(arxiv_id, "failed", "head_fetch_failed")
        print(f"    ❌ --head 失败")
        return {"arxiv_id": arxiv_id, "status": "failed"}

    data["tags"] = tags
    data["fetched_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # Step 2: 优先用 --head section TLDRs
    head_sections = _extract_sections_from_head(data)
    has_head_sections = bool(
        head_sections["key_scientific_questions"] or
        head_sections["core_findings"] or
        head_sections["methods"]
    )

    if has_head_sections:
        # 官方 section 数据质量高，直接使用
        data["key_scientific_questions"] = head_sections["key_scientific_questions"]
        data["core_findings"] = head_sections["core_findings"]
        data["methods"] = head_sections["methods"]
        data["summary_outlook"] = head_sections["summary_outlook"] or data.get("tldr", "")
        data["status"] = "verified"
        cp.set_status(arxiv_id, "verified")
        print(f"    ✅ 完成（head section TLDRs）")
    elif data.get("sections") and not has_head_sections:
        # sections 存在但无匹配节 → 回退 preview（重新获取）
        time.sleep(5)  # 限流
        preview_text, _ = fetch_preview(arxiv_id)
        extra = _extract_sections_from_preview(preview_text or "")
        data["key_scientific_questions"] = extra["key_scientific_questions"]
        data["core_findings"] = extra["core_findings"]
        data["methods"] = extra["methods"]
        if not extra["key_scientific_questions"] and not extra["methods"]:
            tldr = data.get("tldr", "").replace("[research paper]", "").strip()
            if tldr:
                data["key_scientific_questions"] = [tldr]
                data["methods"] = ["详见原文摘要"]
        data["summary_outlook"] = extra["summary_outlook"] or data.get("tldr", "")
        data["status"] = "verified"
        cp.set_status(arxiv_id, "verified")
        print(f"    ✅ 完成（head sections 无效，preview 补充）")
    else:
        # 降级：从 preview 提取
        time.sleep(5)  # 限流
        preview_text, err = fetch_preview(arxiv_id)
        if preview_text:
            extra = _extract_sections_from_preview(preview_text)
            data["key_scientific_questions"] = extra["key_scientific_questions"]
            data["core_findings"] = extra["core_findings"]
            data["methods"] = extra["methods"]
            # preview 解析完全失败 → 用 tldr 降级填充
            # 注意：即使 find 有内容，只要 intro/meth 为空就用 tldr 补充
            if not extra["key_scientific_questions"] and not extra["methods"]:
                tldr = data.get("tldr", "").replace("[research paper]", "").strip()
                if tldr:
                    data["key_scientific_questions"] = [tldr]
                    data["methods"] = ["详见原文摘要"]
            data["summary_outlook"] = extra["summary_outlook"] or data.get("tldr", "")
            data["status"] = "verified"
            cp.set_status(arxiv_id, "verified")
            print(f"    ✅ 完成（abstract + preview）")
        else:
            data["status"] = "partial"
            data["summary_outlook"] = data.get("tldr", "")
            cp.set_status(arxiv_id, "partial", err or "no_preview")
            print(f"    ⚠  仅 head（无 preview）")

    # Step 3: 写入文件
    fp = write_paper(data, OUT_DIR)
    print(f"       → {fp.name}  ({fp.stat().st_size:,} bytes)")
    return data


def main():
    import argparse
    parser = argparse.ArgumentParser(description="deepxiv 论文获取流水线")
    parser.add_argument("--dry", action="store_true", help="仅预览待处理论文")
    parser.add_argument("--priority", type=int, choices=[1, 2], default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--rebuild", action="store_true",
                        help="重新生成所有论文（含已 verified，跳过 checkpoint 过滤）")
    args = parser.parse_args()

    cp = Checkpoint(CKPT_PATH)
    print(f"\n{'='*60}")
    print(f"  deepxiv 论文获取流水线 v6")
    print(f"  输出: {OUT_DIR}")
    print(f"  断点: {CKPT_PATH}")
    print(f"{'='*60}\n")

    todo = [(aid, tags) for aid, tags, pri in MASTER_LIST
            if args.priority is None or pri == args.priority]
    if args.rebuild:
        # 强制重建：忽略 checkpoint，全部重取
        print(f"[重建模式] {len(todo)} 篇全部重取（--rebuild）\n")
    else:
        pending = cp.get_pending([aid for aid, _ in todo])
        todo = [(aid, tags) for aid, tags in todo if aid in pending]

    if args.limit:
        todo = todo[:args.limit]

    print(f"[计划] {len(todo)} 篇待获取 | {cp.report()}\n")
    if args.dry:
        for aid, tags in todo[:20]:
            print(f"  {aid}  {tags}")
        return

    success = partial = failed = 0
    for i, (arxiv_id, tags) in enumerate(todo, 1):
        print(f"\n[{i}/{len(todo)}]", end=" ")
        try:
            result = fetch_one(arxiv_id, tags, cp)
            s = result.get("status", "")
            if s == "verified":   success += 1
            elif s == "partial":  partial += 1
            else:                 failed += 1
        except Exception as e:
            print(f"    🔥 异常: {e}")
            cp.set_status(arxiv_id, "failed", str(e))
            failed += 1

    print(f"\n{'='*60}")
    print(f"  完成！成功 {success} | 部分 {partial} | 失败 {failed}")
    print(f"  {cp.report()}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
