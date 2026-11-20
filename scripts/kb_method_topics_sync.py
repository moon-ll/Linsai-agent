#!/usr/bin/env python3
"""kb_method_topics_sync — 方法专题同步（v7.2.82，入库管线环节）

职责（用户裁决 2026-11-01："方法专题相关流程加入入库流程"）：
    深读 → 方法卡 → 方法页 之后，自动把新增/更新的方法页分类并入
    knowledge/wiki/method-topics/ 对应专题的关联网络，保持
    「专题层 → 原子方法层 → 论文方法卡」三层导航闭合。

    - --sync        扫描 methods/ 未入网方法页 → 分类 → 并入专题（幂等）
    - --status      覆盖统计（专题数/方法页总数/已入网/未入网）
    - --self-check  幂等性与分类自检

    挂载点：deep_read_pipeline.append_today_to_methods_worklist 成功后自动调用；
    也可 CLI 单独跑。状态：memory/method-topics-sync-state.json

设计原则：
    - 零 LLM（关键词强特征规则，优先级从特异到泛化）
    - 幂等（已入网页跳过；重复运行无副作用）
    - 不编造（低密度工作页只入网不扩写）
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from paths import PROJECT_ROOT  # noqa: E402

try:
    from logger import get_logger
    _log = get_logger("kb_method_topics_sync")
except Exception:
    _log = None

METHODS_DIR = PROJECT_ROOT / "knowledge" / "wiki" / "methods"
TOPICS_DIR = PROJECT_ROOT / "knowledge" / "wiki" / "method-topics"
STATE_PATH = PROJECT_ROOT / "memory" / "method-topics-sync-state.json"

# 分类规则（顺序 = 优先级；强特征在前）。与 2026-11-01 全库映射同口径。
RULES = [
    ("固体HHG数值计算方法体系", ["tdse", "sbe", "bloch", "tddft", "dft", "tight-binding", "houston",
                              "floquet", "wannier", "salmon", "密度泛函", "紧束缚", "密度矩阵",
                              "hamiltonian", "布洛赫方程", "贝里曲率反常", "半经典作用量", "量子几何张量"]),
    ("激子与多体效应方法", ["dmft", "exciton", "激子", "doublon", "mott", "rabi", "lamb", "耗散",
                          "lindblad", "加热库", "williams-lax"]),
    ("强场电离量子轨道方法", ["keldysh", "schwinger", "landau-zener", "ivs", "量子轨道", "隧穿电离"]),
    ("阿秒计量方法体系", ["frog", "vmi", "rabbit", "wigner-smith", "pump-probe", "泵浦-探测", "atas",
                        "瞬态吸收", "阿秒瞬态", "少周期", "条纹", "time delay", "时延", "协方差映射",
                        "thz-spectroscopy", "trarpes", "阿秒时钟"]),
    ("多变量光场设计", ["cep门控", "cep稳定", "等离子体镜", "plasma mirror", "涡旋", "vortex", "oam",
                      "泵浦失谐", "波长迁移", "aopdf", "f-2f", "高斯光束", "峰值驱动", "偏振_手性"]),
    ("宏观传播与相位匹配工程", ["截止阶次", "标度律估算", "相位匹配"]),
    ("量子光驱动HHG方法", ["husimi", "bsv", "二阶相干", "光子统计", "联合产额", "压缩光", "层析", "tomography"]),
    ("HHG反演方法学", ["bayesian", "fisher", "cramer", "metropolis", "pinn", "vpinn", "qpinn",
                     "grape", "krotov", "pareto", "最优控制", "mcmc", "贝叶斯", "主动学习",
                     "强化学习", "机器学习控制", "自动微分"]),
    ("对称性与群论选择定则", ["磁点群", "自旋群", "磁性点群", "磁空间群", "磁电耦合", "p波",
                            "空间群", "对称性", "选择定则", "非线性响应张量"]),
    ("材料体系HHG方法", ["moire", "moiré", "莫尔", "bistritzer", "weyl", "stack", "lswt", "自旋波",
                       "滑移", "应变", "chern", "反常霍尔", "mlff", "kagome", "扭转角",
                       "磁各向异性", "磁输运"]),
    ("量子几何量测量方法谱系", ["arpes", "stm", "霍尔", "输运", "circular", "二色", "self-energy",
                             "eliashberg", "弛豫时间"]),
]


def classify(stem: str, text_head: str) -> Optional[str]:
    s = (stem + " " + text_head).lower()
    for topic, kws in RULES:
        for kw in kws:
            if kw.lower() in s:
                return topic
    return None


def _topic_links(topic: str) -> set:
    p = TOPICS_DIR / f"{topic}.md"
    if not p.exists():
        return set()
    return set(re.findall(r"\[\[([^\]|#]+)", p.read_text(encoding="utf-8")))


def _append_links(topic: str, stems: List[str]) -> int:
    p = TOPICS_DIR / f"{topic}.md"
    if not p.exists():
        return 0
    t = p.read_text(encoding="utf-8")
    existing = set(re.findall(r"\[\[([^\]|#]+)", t))
    add = [s for s in stems if s not in existing]
    if not add:
        return 0
    block = "\n".join(f"- [[{s}]]" for s in add)
    t = t.replace("<!-- /linsai-wikilinks -->", f"{block}\n<!-- /linsai-wikilinks -->", 1)
    p.write_text(t, encoding="utf-8")
    return len(add)


def sync(dry_run: bool = False) -> Dict[str, Any]:
    """扫描 methods/ 未入网方法页 → 分类 → 并入专题关联网络（幂等）。"""
    from common import load_json, save_json
    state = load_json(STATE_PATH, default={"linked": {}})
    linked: Dict[str, str] = state.get("linked", {})

    results: Dict[str, Any] = {"scanned": 0, "classified": 0, "appended": 0,
                               "pages": {}, "skipped": []}
    for f in sorted(METHODS_DIR.glob("*.md")):
        stem = f.stem
        results["scanned"] += 1
        if stem in linked and (TOPICS_DIR / f"{linked[stem]}.md").exists():
            if f"[[{stem}]]" in (TOPICS_DIR / f"{linked[stem]}.md").read_text(encoding="utf-8"):
                continue  # 已入网且链接健在
        t = f.read_text(encoding="utf-8")
        topic = classify(stem, t[:1500])
        if topic is None:
            results["skipped"].append(stem)
            continue
        results["classified"] += 1
        results["pages"][stem] = topic
        if not dry_run:
            n = _append_links(topic, [stem])
            results["appended"] += n
            linked[stem] = topic
    if not dry_run:
        state["linked"] = linked
        state["updated_at"] = __import__("common").now_utc()
        save_json(STATE_PATH, state)
    return results


def status() -> Dict[str, Any]:
    from common import load_json
    state = load_json(STATE_PATH, default={"linked": {}})
    total = len(list(METHODS_DIR.glob("*.md")))
    topics = sorted(p.stem for p in TOPICS_DIR.glob("*.md"))
    return {"topics": len(topics), "topic_names": topics, "methods_total": total,
            "linked_in_state": len(state.get("linked", {})),
            "note": "覆盖数以 --sync 实跑为准（含未走状态文件的链接）"}


def _self_check() -> None:
    assert classify("TDSE求解器", "多带含时薛定谔方程") == "固体HHG数值计算方法体系"
    assert classify("bayesian-inference", "贝叶斯后验采样") == "HHG反演方法学"
    assert classify("不存在的页", "无关内容") is None
    r = sync(dry_run=True)
    assert "scanned" in r and "classified" in r
    # 幂等性：dry-run 不落盘
    s1 = sync(dry_run=True)
    s2 = sync(dry_run=True)
    assert s1["scanned"] == s2["scanned"]
    print("✓ kb_method_topics_sync 自检通过")


def main() -> None:
    ap = argparse.ArgumentParser(description="方法专题同步（入库管线环节）")
    ap.add_argument("--sync", action="store_true", help="扫描并入专题（幂等）")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()
    if args.self_check:
        _self_check()
        return
    if args.status:
        import json
        print(json.dumps(status(), ensure_ascii=False, indent=1))
        return
    r = sync(dry_run=args.dry_run)
    print(f"○ 方法专题同步：扫描 {r['scanned']} 页，分类 {r['classified']}，"
          f"并入链接 {r['appended']}（dry_run={args.dry_run}）")
    if r["skipped"]:
        print(f"  未分类 {len(r['skipped'])} 页（低密度/无关页，保持工作页状态）")


if __name__ == "__main__":
    main()
