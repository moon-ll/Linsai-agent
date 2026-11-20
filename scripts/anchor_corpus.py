#!/usr/bin/env python3
"""锚集（Anchor Corpus）——真实获资助项目书校准库（v7.2.69，定案2 收官件）。

用法：
    python3 scripts/anchor_corpus.py --ingest        # 解析 references/anchors/ 入库
    python3 scripts/anchor_corpus.py --list          # 列锚点
    python3 scripts/anchor_corpus.py --compare <proposal_id> [--module rationale]
    python3 scripts/anchor_corpus.py --self-check

锚集是治 Goodhart 的根本手段：机器分可漂移，真实中标本子不会。pairwise
对比（交换顺序双跑防位置偏差）替代绝对分数线：「我们的立项依据比锚集
中这本中标书强还是弱、差在哪」。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from common import now_utc  # noqa: E402
from paths import PROJECT_ROOT  # noqa: E402

ANCHOR_DIR = PROJECT_ROOT / "references" / "anchors"
ANCHOR_DB = ANCHOR_DIR / "anchor-db.json"
# v7.2.75 并入的真实成功范本目录（模块级常量：测试可 patch 隔离，
# 否则 ingest() 在测试环境会静默并入真实范本，破坏确定性）
TEMPLATES_DIR = PROJECT_ROOT / "references" / "nsfc-templates"

# 项目书模块标题模式（兼容常见写法）
MODULE_PATTERNS = {
    "rationale": r"(?:立项依据|研究意义与国内外现状|项目的立项依据)",
    "content": r"(?:研究内容|项目的研究内容|研究目标与研究内容)",
    "scheme": r"(?:研究方案|研究方法与技术路线|拟采取的研究方案)",
}
MODULE_ORDER = ["rationale", "content", "scheme"]


def _extract_text(path: Path) -> str:
    """docx/pdf/md/txt 统一抽文本（尽力而为，失败返回空）。

    v7.2.72 修复（BUG-30/31/32）：

    - **docx**（BUG-30）：旧版用 `re.sub(r"<[^>]+>", "", xml)` 直接剥标签，
      段落之间**没有换行**——`_split_modules` 的标题正则用 `^`（re.M 行首
      锚定）匹配，段落被连成一坨后除首段外全部匹配不到 → docx 锚点切出
      0 个模块（实测）。改为剥标签前先把 `</w:p>` 还原成换行。
    - **pdf**（BUG-31）：系统 python3 没有 pdfminer，`pdftotext` 也未安装
      → 旧版恒返回空串，PDF 锚点在 ingest 阶段被 `if not text.strip()`
      直接跳过。改为复用项目既有三级降级抽取链路
      （`pdf_manager.PDFManager.get_or_extract_text` → venv pypdf 抽取器）。
    """
    try:
        if path.suffix.lower() in (".md", ".txt"):
            return path.read_text(encoding="utf-8", errors="ignore")
        if path.suffix.lower() == ".docx":
            import zipfile
            with zipfile.ZipFile(path) as z:
                xml = z.read("word/document.xml").decode("utf-8", errors="ignore")
            # 段落边界还原成换行——否则标题正则的 ^ 锚定全部落空
            xml = re.sub(r"</w:p>", "\n", xml)
            xml = re.sub(r"<w:br[^>]*/>", "\n", xml)
            return re.sub(r"<[^>]+>", "", xml)
        if path.suffix.lower() == ".pdf":
            return _extract_pdf_text(path)
    except Exception:
        return ""
    return ""


def _extract_pdf_text(path: Path) -> str:
    """PDF 抽文本（三级降级，复用项目既有链路）。

    v7.2.72 修复（BUG-31）：系统 python3 没有 pdfminer、`pdftotext` 也未
    安装 → 旧版恒返回空串，PDF 锚点在 ingest 阶段被 `if not text.strip()`
    直接跳过。改为复用项目既有抽取器
    （`deepxiv_knowledge/pypdf_extract_local.py`，走带 pypdf 的 venv 解释器）。

    1. venv 解释器 + pypdf 抽取器（项目既有首选路径）
    2. 本进程 pdfminer（解释器自带时可用）
    3. 系统 `pdftotext`
    """
    # 1. venv pypdf 抽取器（项目既有首选，pdf_manager 同款策略）
    try:
        import subprocess

        extractor = SCRIPTS_DIR / "deepxiv_knowledge" / "pypdf_extract_local.py"
        candidates = [
            str(Path.home() / ".venv" / "bin" / "python3"),
            "python3",
        ]
        for py_exe in candidates:
            if not (Path(py_exe).exists() if os.sep in py_exe else _which(py_exe)):
                continue
            if not extractor.exists():
                break
            result = subprocess.run(
                [py_exe, str(extractor), str(path)],
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            break
    except Exception:
        pass
    # 2. 本进程 pdfminer（解释器自带时可用）
    try:
        import pdfminer.high_level as hl

        return hl.extract_text(str(path)) or ""
    except Exception:
        pass
    # 3. 系统 pdftotext
    try:
        import subprocess

        result = subprocess.run(
            ["pdftotext", "-q", str(path), "-"],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return ""


def _which(cmd: str) -> Optional[str]:
    """shutil.which 的轻量替身（避免顶层 import）。"""
    import shutil

    return shutil.which(cmd)


def _split_modules(text: str) -> Dict[str, str]:
    """按模块标题模式切段（标题层级 1-3 均可）。"""
    modules: Dict[str, str] = {}
    positions = []
    for key, pat in MODULE_PATTERNS.items():
        # 行首可带 markdown 井号或「（一）」式序号前缀
        rx = re.compile(rf"^[#\s（(一二三四五六七八九十0-9、.（）()]*{pat}", re.M)
        m = rx.search(text)
        if m:
            positions.append((m.start(), key))
    positions.sort()
    for idx, (pos, key) in enumerate(positions):
        end = positions[idx + 1][0] if idx + 1 < len(positions) else len(text)
        modules[key] = text[pos:end].strip()[:20000]
    return modules


def ingest(source_dir: Optional[Path] = None) -> Dict[str, Any]:
    """解析锚点文档入库。

    v7.2.75: 默认扫 references/anchors/（专用收料位）；另自动并入
    references/nsfc-templates/*-正文.md——用户提供的 3 份真实成功范本
    （面上/青年/原创探索，8 月入库、nsfc-standards style_benchmark 即
    提炼自此），它们就是锚集的第一批成员。
    """
    sources = [source_dir] if source_dir else [ANCHOR_DIR]
    if not source_dir:
        if TEMPLATES_DIR.exists():
            sources.append(TEMPLATES_DIR)
    db: Dict[str, Any] = {"anchors": [], "updated_at": now_utc()}
    seen = set()
    for src in sources:
        if not src or not src.exists():
            continue
        for f in sorted(src.iterdir()):
            if f.name in seen:
                continue
            seen.add(f.name)
            if f.name.startswith(".") or f.name == ANCHOR_DB.name or not f.is_file():
                continue
            text = _extract_text(f)
            if not text.strip():
                continue
            modules = _split_modules(text)
            db["anchors"].append({
                "file": f.name,
                "chars": len(text),
                "modules": {k: len(v) for k, v in modules.items()},
                "text_path": _save_text(f.name, text, modules),
            })
    db["updated_at"] = now_utc()
    (ANCHOR_DIR / "anchor-db.json").write_text(
        json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
    return db


def _save_text(name: str, text: str, modules: Dict[str, str]) -> str:
    outdir = ANCHOR_DIR / "parsed"
    outdir.mkdir(parents=True, exist_ok=True)
    stem = re.sub(r"[^\w.-]", "_", name)
    (outdir / f"{stem}.json").write_text(
        json.dumps({"full": text[:60000], "modules": modules},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    return f"parsed/{stem}.json"


def load_anchors() -> List[Dict[str, Any]]:
    if not ANCHOR_DB.exists():
        return []
    try:
        db = json.loads(ANCHOR_DB.read_text(encoding="utf-8"))
        return db.get("anchors", [])
    except Exception:
        return []


def _load_module_text(anchor: Dict[str, Any], module: str) -> str:
    try:
        data = json.loads((ANCHOR_DIR / anchor["text_path"]).read_text(encoding="utf-8"))
        return (data.get("modules") or {}).get(module, "")
    except Exception:
        return ""


def pairwise_compare(ours_text: str, anchor_text: str, module: str) -> Optional[Dict[str, Any]]:
    """交换顺序双跑的 pairwise 对比（防位置偏差）。返回 {verdict, gap_points}。

    verdict 三值：ours_stronger / comparable / anchor_stronger
    """
    from llm_gateway import llm_complete
    sys_p = (
        "你是 NSFC 基金评审专家，对两份同模块文本做对比评审。只输出 JSON："
        '{"verdict": "A更强|相当|B更强", "gap_points": ["B 相对 A 的主要差距点，最多3条，每条一句"]}'
        "。verdict 以论证密度/数值链可溯源性/创新点实质为准，不受篇幅与文采影响。"
    )
    results = []
    # v7.2.73 修复（BUG-33）：归一化方向反转。
    # 旧版两轮都用 ("A", ...) 开头，靠 `order[0] == "A"` 判定「A 槽是我方」——
    # 但第 2 轮 A 槽装的是**锚点**，`a_is_ours` 恒为 True → 第 2 轮的
    # 「B更强」（B=我方）被反向归一化成 anchor_stronger。后果：
    #   ① LLM 判定「我方更强」时，两轮归一化结果不一致 → 保守取弱 →
    #      最终恒为 anchor_stronger（「我方更强」这一最有价值的结论**永远
    #      无法产出**）；
    #   ② 位置偏置检出能力反向失效——恒判「A更强」的偏置 LLM 被归一化为
    #      「我方更强」，恰好把双跑设计要防的情况断言成了正面结论。
    # 修复：显式传 `a_is_ours` 布尔量，不再从位置字符串反推。
    for a_is_ours, a_text, b_text in ((True, ours_text, anchor_text),
                                      (False, anchor_text, ours_text)):
        try:
            # v7.2.72 修复（BUG-32）：`llm_complete` 返回三元组
            # `(ok, text, meta)`——旧版把整个三元组当字符串塞进
            # `re.search(r"\{.*\}", raw)`，必然抛 TypeError
            # （"expected string or bytes-like object"）→ 异常被
            # `except Exception: continue` 吞掉 → **每一次对比都静默失败**，
            # `pairwise_compare` 恒返回 None（实测：LLM 返回合法 JSON 时
            # 结果仍为 None）。改为正确解包三元组。
            ok, text, _meta = llm_complete(
                system_prompt=sys_p,
                user_prompt=f"【A】\n{a_text[:6000]}\n\n【B】\n{b_text[:6000]}\n\n"
                            f"对比模块：{module}。输出 JSON。",
                prefer="governance", timeout=90)
            if not ok or not (text or "").strip():
                continue
            m = re.search(r"\{.*\}", text, re.S)
            if not m:
                continue
            data = json.loads(m.group(0))
            v = data.get("verdict", "")
            if v in ("A更强", "B更强", "相当"):
                # 归一化到「我方视角」
                if v == "相当":
                    results.append(("comparable", data.get("gap_points", [])))
                elif (v == "A更强") == a_is_ours:
                    results.append(("ours_stronger", data.get("gap_points", [])))
                else:
                    results.append(("anchor_stronger", data.get("gap_points", [])))
        except Exception:
            continue
    if not results:
        return None
    verdicts = [r[0] for r in results]
    # 双跑不一致 → 保守取弱
    if len(set(verdicts)) > 1:
        order_rank = {"anchor_stronger": 0, "comparable": 1, "ours_stronger": 2}
        verdict = min(verdicts, key=lambda v: order_rank[v])
    else:
        verdict = verdicts[0]
    # v7.2.98: gap_points 只取与最终 verdict 同方向的跑——双跑不一致保守
    # 取弱时，另一跑（方向相反）的 gap 描述的其实是「锚点的差距」，混入后
    # 产生"挂起理由却说锚点不及我方"的自相矛盾文本（2026-11-04 adopt
    # 首战实证：houston/ssh-weyl/attosecond 三课题挂起理由均混入反向描述）。
    same_dir_gaps = []
    for v, g in results:
        if v != verdict:
            continue
        for item in (g or [])[:3]:
            if item and item not in same_dir_gaps:
                same_dir_gaps.append(item)
    return {"verdict": verdict, "gap_points": same_dir_gaps[:5]}


def compare_proposal(proposal_id: str, module: str = "rationale") -> Optional[Dict[str, Any]]:
    """我方课题某模块 vs 全部锚点同模块，取最严 verdict（保守）。"""
    anchors = load_anchors()
    if not anchors:
        return None
    # v7.2.75: 显式逐阶段定位——find_proposal_dir 对 pending_review 课题
    # 解析到 optimizing 残留路径（sections 不存在→静默 None，实测 ssh-weyl）
    root = PROJECT_ROOT / "research_proposals"
    prop_dir = None
    for stage in ("optimizing", "pending_review", "archived"):
        cand = root / stage / proposal_id
        if (cand / "04_proposal" / "sections" / f"{module}.md").exists():
            prop_dir = cand
            break
    if prop_dir is None:
        return None
    sec = prop_dir / "04_proposal" / "sections" / f"{module}.md"
    ours = sec.read_text(encoding="utf-8")
    per_anchor = []
    final = None
    rank = {"anchor_stronger": 0, "comparable": 1, "ours_stronger": 2}
    for a in anchors:
        atext = _load_module_text(a, module)
        if not atext:
            continue
        r = pairwise_compare(ours, atext, module)
        if r:
            per_anchor.append({"anchor": a["file"], **r})
            if final is None or rank[r["verdict"]] < rank[final["verdict"]]:
                final = r | {"anchor": a["file"]}
    if not per_anchor:
        return None
    return {"module": module, "final": final, "per_anchor": per_anchor}


def _self_check() -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        global ANCHOR_DIR, ANCHOR_DB
        old = ANCHOR_DIR
        ANCHOR_DIR = Path(td)
        ANCHOR_DB = ANCHOR_DIR / "anchor-db.json"
        (ANCHOR_DIR / "a.md").write_text(
            "# 立项依据\n\n锚点论证。" * 50 + "\n# 研究内容\n\n锚点内容。\n# 研究方案\n\n锚点方案。",
            encoding="utf-8")
        db = ingest(Path(td))  # 显式单源，隔离真实范本目录
        assert len(db["anchors"]) == 1 and "rationale" in db["anchors"][0]["modules"], db
        assert len(load_anchors()) == 1
        # 空 txt 不入库
        (ANCHOR_DIR / "empty.txt").write_text("", encoding="utf-8")
        db = ingest(Path(td))
        assert len(db["anchors"]) == 1
        # pairwise 归一化逻辑（mock 三态）
        ANCHOR_DIR = old
        ANCHOR_DB = ANCHOR_DIR / "anchor-db.json"
    print("✓ anchor_corpus 自检通过")


def main() -> None:
    parser = argparse.ArgumentParser(description="锚集：真实中标本子校准库")
    parser.add_argument("--ingest", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--compare", metavar="PID")
    parser.add_argument("--module", default="rationale")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    if args.self_check:
        _self_check()
    elif args.ingest:
        db = ingest()
        print(f"✓ 入库 {len(db['anchors'])} 个锚点：",
              [(a["file"], a["modules"]) for a in db["anchors"]])
    elif args.list:
        for a in load_anchors():
            print(f"- {a['file']}（{a['chars']} 字，模块 {a['modules']}）")
    elif args.compare:
        r = compare_proposal(args.compare, args.module)
        print(json.dumps(r, ensure_ascii=False, indent=2) if r else "（无锚点或无该模块）")


if __name__ == "__main__":
    main()
