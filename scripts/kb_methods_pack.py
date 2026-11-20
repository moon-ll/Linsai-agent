#!/usr/bin/env python3
"""课题方法素材包生成（v7.0.6 批次三，v7.2.30 wikilink 节点格式）。

对每个活跃课题（optimizing/pending_review/drafts），按其 00 号设想的
方法关键词匹配 KB 方法页 + 论文页方法卡（methods-backfill 产物），
生成 03_method/kb-methods-pack.md 素材包。

v7.2.30 重大改造（消费端断链修复）：
    旧版输出是"摘要包"格式（每条 1-2KB 文本块），writer prompt 注入后
    仅作"参考文本"使用，方案不强制引用——11 课题对 KB 94 个方法页的
    wikilink 引用 = 0（P0-2 评估）。
    新版改写为"wikilink 节点"格式：
        - 每个方法页/论文卡条目用 `[[方法页slug]]` 显式节点引用
        - 参数表行后追加 `[[出处:xxx]]` 引用
        - writer 落盘后用 `kb_pack_wikilink_guard.py` 校验：
            0 引用 = 警告、< 3 引用 = 不达标
    消费端从"参考文本"升级为"可被 Obsidian 双向链接索引的节点"。

用法：
    python3 scripts/kb_methods_pack.py                    # 全部活跃课题
    python3 scripts/kb_methods_pack.py --proposal <id>    # 指定课题
    python3 scripts/kb_methods_pack.py --self-check

规范：仅标准库；零 LLM（检索 + 文件聚合）；写走原子写。
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

from common import load_json, now_utc, save_json
from paths import PROJECT_ROOT

try:
    from logger import get_logger
    _log = get_logger("kb_methods_pack")
except Exception:
    _log = None

LIFECYCLE_PATH = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"
METHODS_DIR = PROJECT_ROOT / "knowledge" / "wiki" / "methods"
METHOD_TOPICS_DIR = PROJECT_ROOT / "knowledge" / "wiki" / "method-topics"
PAPERS_DIR = PROJECT_ROOT / "knowledge" / "wiki" / "papers"
BACKFILL_MARKER = "<!-- methods-backfill:v1 -->"
STAGES = ("optimizing", "pending_review", "drafts")

# 方法关键词启发式（英文方法缩写 + 中文方法词，与 backfill 同口径扩展）
_KW_EN = (r"\b(?:HHG|TDDFT|SBE|TDSE|FROG|RABBITT|VMI|COLTRIMS|MOCVD|CVD|MBE"
          r"|DFT|THz|XUV|OAM|SHG|Floquet|Berry|RPA|DMFT|Kubo|PINN)\b")
_KW_CN = r"[一-龥]{2,6}(?:光谱|谱学|测量|探测|计算|模拟|沉积|外延|解理|泵浦|调控|方法|装置|技术)"


def _proposal_ids(only: Optional[str] = None) -> List[str]:
    lc = load_json(LIFECYCLE_PATH, default={})
    out = []
    for pid, st in (lc.get("proposals") or {}).items():
        if only and pid != only:
            continue
        if st.get("status") in STAGES:
            out.append(pid)
    return out


def _prop_dir(pid: str, status: str) -> Optional[Path]:
    d = PROJECT_ROOT / "research_proposals" / status / pid
    return d if d.exists() else None


def _idea_text(prop_dir: Path) -> str:
    # 优先读 00_research_idea.md（设想正文，含方法关键词）；缺失再回退到 00_proposal-brief.md。
    # v7.0.8 修复：原版按文件名排序先取 brief 决策包，前 4000 字全是元数据/历史表，导致
    # 关键词提取为零、素材包生成失败。本修正让真正含方法关键词的设想正文优先被读取。
    for name in ("00_research_idea.md", "00_proposal-brief.md"):
        p = prop_dir / name
        if p.exists():
            try:
                return p.read_text(encoding="utf-8")[:4000]
            except Exception:
                continue
    return ""


def _keywords(text: str) -> List[str]:
    kws = set(re.findall(_KW_EN, text))
    kws.update(re.findall(_KW_CN, text))
    return sorted(kws)


def _match_method_pages(kws: List[str], top: int = 8) -> List[Dict[str, str]]:
    """按关键词匹配方法页（标题/别名/正文命中计分，零 LLM）。"""
    scored: Dict[str, int] = {}
    for f in METHODS_DIR.glob("*.md"):
        try:
            t = f.read_text(encoding="utf-8")
        except Exception:
            continue
        if "merged_into:" in t[:1200]:
            continue  # 跳过 stub（frontmatter 含 merged_into，可能位于
                      # tags/related 等长字段之后）
        score = 0
        for kw in kws:
            if kw.lower() in f.stem.lower():
                score += 3
            head = t[:1500].lower()
            if kw.lower() in head:
                score += 2
        if score:
            scored[f.stem] = score
    ranked = sorted(scored, key=lambda k: -scored[k])[:top]
    out = []
    for stem in ranked:
        t = (METHODS_DIR / f"{stem}.md").read_text(encoding="utf-8")
        title_m = re.search(r'^title:\s*"([^"]+)"', t, re.M)
        # 摘原理+参数表头几行（手册吸收够用的最小单元）
        body = re.sub(r"\A---\n.*?\n---\n", "", t, flags=re.S)
        pm = re.search(r"## 原理\n+(.{0,400})", body, re.S)
        out.append({
            "stem": stem,
            "title": title_m.group(1) if title_m else stem,
            "digest": (pm.group(1).strip() if pm else body[:300]).replace("\n", " ")[:400],
        })
    return out


def _match_method_topics(kws: List[str], top: int = 6) -> List[Dict[str, str]]:
    """v7.2.77: 匹配方法专题页（method-topics，测量目标型谱系/选型层，零 LLM）。

    计分口径同方法页（标题×3 + 头部×2）；digest 取专题定位行（blockquote 首段），
    保证 writer 在素材包里直接看到该专题回答什么问题、服务哪些章节。
    """
    if not METHOD_TOPICS_DIR.exists():
        return []
    scored: Dict[str, int] = {}
    for f in METHOD_TOPICS_DIR.glob("*.md"):
        try:
            t = f.read_text(encoding="utf-8")
        except Exception:
            continue
        score = 0
        for kw in kws:
            if kw.lower() in f.stem.lower():
                score += 3
            if kw.lower() in t[:1500].lower():
                score += 2
        if score:
            scored[f.stem] = score
    ranked = sorted(scored, key=lambda k: -scored[k])[:top]
    out = []
    for stem in ranked:
        t = (METHOD_TOPICS_DIR / f"{stem}.md").read_text(encoding="utf-8")
        title_m = re.search(r'^title:\s*"([^"]+)"', t, re.M)
        body = re.sub(r"\A---\n.*?\n---\n", "", t, flags=re.S)
        # 专题定位 = 正文 blockquote 首段（回答什么问题/服务哪些章节）
        bm = re.search(r"^>\s*\*\*专题定位\*\*：(.{0,300})", body, re.M)
        digest = (bm.group(1).strip() if bm else body[:300]).replace("\n", " ")[:400]
        out.append({"stem": stem,
                    "title": title_m.group(1) if title_m else stem,
                    "digest": digest})
    return out


def _match_paper_cards(kws: List[str], top: int = 6) -> List[Dict[str, str]]:
    """匹配带方法卡的论文页（BACKFILL_MARKER 页优先，零 LLM）。"""
    out = []
    kws_low = [k.lower() for k in kws]
    for f in PAPERS_DIR.glob("*.md"):
        try:
            t = f.read_text(encoding="utf-8")
        except Exception:
            continue
        if BACKFILL_MARKER not in t:
            continue
        score = sum(2 for k in kws_low if k in t[:6000].lower())
        if not score:
            continue
        m = re.search(r"## 研究方法（方法卡）\n(.*?)(?=\n## |\Z)", t, re.S)
        if not m:
            continue
        card = m.group(1)
        pm = re.search(r"\*\*方法\*\*：(.+)", card)
        params = re.findall(r"^\| (.+?) \|", card, re.M)[:4]
        out.append({
            "page": f.stem,
            "method": (pm.group(1) if pm else "")[:120],
            "params_sample": "；".join(p.strip() for p in params if p.strip())[:300],
            "score": score,
        })
        if len(out) >= 40:
            break
    out.sort(key=lambda x: -x["score"])
    return out[:top]


def generate_pack(pid: str, dry_run: bool = False) -> Dict[str, Any]:
    """为课题生成/刷新方法素材包。"""
    lc = load_json(LIFECYCLE_PATH, default={})
    st = (lc.get("proposals") or {}).get(pid, {})
    status = st.get("status", "optimizing")
    prop_dir = _prop_dir(pid, status)
    if not prop_dir:
        return {"pid": pid, "ok": False, "error": "课题目录不存在"}
    idea = _idea_text(prop_dir)
    kws = _keywords(idea)
    if not kws:
        return {"pid": pid, "ok": False, "error": "未提取到方法关键词"}
    pages = _match_method_pages(kws)
    topics = _match_method_topics(kws)
    cards = _match_paper_cards(kws)

    lines = [
        f"# 课题方法素材包（KB 自动聚合，v7.2.30 wikilink 节点格式）",
        "",
        f"- 课题：{pid}",
        f"- 生成时间：{now_utc()}",
        f"- 方法关键词：{'、'.join(kws[:14])}",
        "",
        "> 用途：update_method_manual / writer 写方案时的可实施细节来源。",
        "> **v7.2.30 起改 wikilink 节点格式**：每条方法/参数都附 `[[方法页slug]]` 双向链接，",
        "> writer 落盘后由 `kb_pack_wikilink_guard.py` 校验（≥3 引用为达标）。",
        "> 参数必须按参数溯源纪律标注来源；本包为 KB 索引摘要，取参数前读对应页原文。",
        "",
    ]
    # v7.2.77: 方法专题节（测量目标型谱系/选型层）——立项依据与方案选型的骨架素材
    if topics:
        lines.append(f"## 〇、方法专题（{len(topics)}，谱系/选型层）")
        lines.append("")
        for tp in topics:
            lines.append(f"### [[method-topics/{tp['stem']}|{tp['title']}]]")
            lines.append(f"页：knowledge/wiki/method-topics/{tp['stem']}.md")
            lines.append(f"专题定位：{tp['digest']}")
            lines.append("")
    lines.append(f"## 一、匹配的知识库方法页（{len(pages)}）")
    lines.append("")
    # v7.2.30: 改 wikilink 节点格式——每条用 `[[slug]]` 显式引用
    for p in pages:
        lines.append(f"### [[methods/{p['stem']}|{p['title']}]]")
        lines.append(f"页：knowledge/wiki/methods/{p['stem']}.md")
        lines.append(f"摘要：{p['digest']}")
        lines.append("")
    lines.append(f"## 二、带方法卡的论文页（{len(cards)}）")
    lines.append("")
    for c in cards:
        lines.append(f"### [[papers/{c['page']}|{c['method'] or c['page']}]]")
        lines.append(f"页：knowledge/wiki/papers/{c['page']}.md")
        if c["params_sample"]:
            lines.append(f"参数样例：{c['params_sample']}")
        lines.append("")
    content = "\n".join(lines)
    out_path = prop_dir / "03_method" / "kb-methods-pack.md"
    if not dry_run:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
    return {"pid": pid, "ok": True, "pages": len(pages), "cards": len(cards),
            "kws": len(kws), "path": str(out_path.relative_to(PROJECT_ROOT))}


def run(only: Optional[str] = None, dry_run: bool = False) -> None:
    pids = _proposal_ids(only)
    print(f"○ 课题方法素材包生成（{len(pids)} 个课题{'，dry-run' if dry_run else ''}）")
    ok_n = 0
    for pid in pids:
        r = generate_pack(pid, dry_run=dry_run)
        if r.get("ok"):
            ok_n += 1
            print(f"  ✓ {pid[:48]:48} 方法页 {r['pages']} + 论文卡 {r['cards']}（关键词 {r['kws']}）")
        else:
            print(f"  ✗ {pid[:48]:48} {r.get('error', '')}")
    print(f"{'✓' if not dry_run else '○'} 完成 {ok_n}/{len(pids)}")


def _self_check() -> int:
    failures = []
    # 关键词提取
    kws = _keywords("利用 HHG 光谱学与 THz 泵浦探测测量交变磁体自旋劈裂，配合 TDDFT 模拟。")
    if "HHG" not in kws or "TDDFT" not in kws:
        failures.append(f"英文关键词漏提: {kws}")
    if not any("测量" in k or "模拟" in k for k in kws):
        failures.append(f"中文关键词漏提: {kws}")
    # stub 页排除
    stub = PROJECT_ROOT / "knowledge" / "wiki" / "methods" / "磁性空间群群论对称性分析.md"
    if stub.exists():
        t = stub.read_text(encoding="utf-8")
        if "merged_into:" in t[:400] and _match_method_pages(["磁性空间群"], top=20):
            hits = [x["stem"] for x in _match_method_pages(["磁性空间群"], top=20)]
            if "磁性空间群群论对称性分析" in hits:
                failures.append("stub 页未被排除")
    if failures:
        for x in failures:
            print(f"✗ {x}")
        return 1
    print("✓ kb_methods_pack 自检通过")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="课题方法素材包生成")
    parser.add_argument("--proposal", type=str, default="", help="指定课题 id")
    parser.add_argument("--dry-run", action="store_true", help="预览不落盘")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args(argv)
    if args.self_check:
        return _self_check()
    run(only=args.proposal or None, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
