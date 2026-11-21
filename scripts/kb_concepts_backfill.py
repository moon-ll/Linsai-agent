#!/usr/bin/env python3
"""
kb_concepts_backfill.py — 知识库概念层扩容发射器（零 LLM）

用途：
    解决知识库"概念层薄弱"短板（评估 2026-10-03：concepts 66 页 vs papers
    2340 页，悬空 wikilink 1857 个目标，其中排除课题 ID 后真实概念缺口
    约 200+，高频者如 高次谐波产生（HHG）208 次、Corkum 64 次）。

    本脚本只做确定性扫描与清单发射（与 kb_methods_backfill 的 v7.0.7
    用户裁决模式一致：回补任务由 ZCode 执行，不挂 cron、不内置 LLM）。

三个功能：
    1. --scan              扫描悬空 wikilink，输出频次排行（预览）
    2. --worklist N        发射概念撰写工作清单（memory/concepts-backfill-worklist.json），
                           ZCode 任务按清单撰写概念页（须过 kb_wiki v7.1.3 质量门）
    3. --graduate          方法卡毕业扫描：同名方法卡出现 ≥3 次且无独立方法页
                           → 发射毕业清单（memory/methods-graduate-worklist.json），
                           ZCode 撰写独立方法页（四要素 + 参数溯源纪律）

用法示例：
    python3 scripts/kb_concepts_backfill.py --scan
    python3 scripts/kb_concepts_backfill.py --worklist 150
    python3 scripts/kb_concepts_backfill.py --graduate
    python3 scripts/kb_concepts_backfill.py --self-check

约束：
    - 仅使用 Python 3 标准库
    - 路径使用 pathlib.Path，PROJECT_ROOT 经 Path(__file__).parent.parent 推导
    - 零 LLM：全部为确定性统计
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from common import now_utc, save_json  # noqa: E402

WIKI_PAPERS = PROJECT_ROOT / "knowledge" / "wiki" / "papers"
WIKI_CONCEPTS = PROJECT_ROOT / "knowledge" / "wiki" / "concepts"
WIKI_METHODS = PROJECT_ROOT / "knowledge" / "wiki" / "methods"
# 真实格式：knowledge/aliases.json，key=规范概念名，value=[别名...]
ALIASES_PATH = PROJECT_ROOT / "knowledge" / "aliases.json"
CONCEPTS_WORKLIST = PROJECT_ROOT / "memory" / "concepts-backfill-worklist.json"
GRADUATE_WORKLIST = PROJECT_ROOT / "memory" / "methods-graduate-worklist.json"

# 课题/运维 ID 模式——不是概念缺口
_PROPOSAL_ID_RE = re.compile(r"^(general-|key-|PRJ-|UNIT-|cl_\d{8}_)")

# 纯年份/编号/URL 噪声
_NOISE_RE = re.compile(r"^(\d{4}|\d{4}[.)）]?|https?://|[a-z]+-\d{4}\.\d+)$", re.I)

# v7.2.16 净化规则（用户裁决：知识库巡检移交前清洗发射清单）
# 人名启发式：纯首字母大写西文单词（Corkum/Krausz/Keldysh……人物不属概念层）
_PERSON_NAME_RE = re.compile(r"^[A-Z][a-z]{2,}$")
# arXiv ID 裸引用（2607.19937）
_ARXIV_ID_RE = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$")


def _is_noise_concept(name: str) -> bool:
    """悬空 wikilink 噪音判定（零 LLM，确定性）。

    剔除七类：
      1. 深读笔记标题（[[论文精读：...]] 指向笔记页的标题变体链接）
      2. 项目标签（NSFC- 前缀）
      3. 人名（纯首字母大写西文单词）
      4. 裸 arXiv ID
      5. 英文论文标题（西文长串 ≥4 空格，无中文）
      6. 中文论文标题（含「——」；或含「：/作为」且长度达标题量级）
      7. 同义变体经 CONCEPT_SYNONYMS 归一（在 scan 内处理）
      8. 纯数字（v7.2.45）：文献引用角标 [[46]] 被误当概念建页，
         frontmatter `title: 46` 经类型推断成 int，下游 .lower() 崩溃
    """
    if "论文精读" in name or name.startswith("NSFC-"):
        return True
    if _PERSON_NAME_RE.match(name):
        return True
    if _ARXIV_ID_RE.match(name):
        return True
    has_cjk = bool(re.search(r"[\u4e00-\u9fff]", name))
    cjk_n = len(re.findall(r"[\u4e00-\u9fff]", name))
    if not has_cjk and len(name.split()) >= 4:
        return True
    if "——" in name:
        return True
    if ("：" in name and cjk_n >= 10) or ("作为" in name and cjk_n >= 12):
        return True
    # 公式/数学符号噪音（Δ/2,f_k 之类）
    if re.match(r"^[Δ∂∫∇ΣΩ]", name):
        return True
    # v7.2.45：纯数字（引用角标 [[46]] / 数值 token）——不是概念。
    # 建页后 frontmatter `title: 46` 被类型推断成 int，frontmatter 解析器
    # 与 kb_health_weekend / kb_merger 的 .lower() 消费方直接崩。
    if re.fullmatch(r"\d+(?:\.\d+)?", name):
        return True
    return False


# 同义词归一表：变体 → 规范名（频次累计到规范名，避免 ZCode 重复建页）
CONCEPT_SYNONYMS = {
    "谷电子学": "能谷电子学",          # 对齐 MOC 分类名「能谷电子学」
    "Rashba自旋轨道耦合": "Rashba效应",
    "PINN（物理信息神经网络）": "物理信息神经网络（PINN）",   # 括号序颠倒变体
    "nonlinear Hall effect": "非线性霍尔效应",                # 中英同义
    "高次谐波产生HHG": "高次谐波产生",                        # 已存在页的简写变体
}

# 通用方法词表（领域方法关键词；论文方法卡描述 per-paper 几乎全唯一，
# 同名统计无意义——改按通用方法词在卡片正文的提及频次毕业）
COMMON_METHOD_TERMS = [
    "TDSE", "Lewenstein", "TDDFT", "DFT", "BSE", "PIC", "GPW",
    "RABBITT", "attosecond streaking", "阿秒条纹", "VMI", "COLTRIMS",
    "泵浦探测", "瞬态吸收", "高次谐波光谱", "EUV 光谱", "ARPES",
    "时间分辨光电子", "库仑修正", "强场近似", "两步模型", "三步模型",
    "费米面提取", "Berry 曲率", "陈数", "非线性光学系数",
]

_METHOD_CARD_MARK = "（方法卡）"


def scan_method_graduation(min_shared: int = 3) -> List[Dict[str, Any]]:
    """方法卡毕业扫描：通用方法词在论文方法卡中提及 ≥min_shared 次且无独立方法页。

    论文方法卡描述 per-paper 几乎全唯一（实测 1206/1217 不同名），
    故毕业锚点用 COMMON_METHOD_TERMS 通用方法词表统计提及页数。
    ZCode 按清单撰写独立方法页（原理/参数表/适用边界/代表作 四要素，
    参数溯源纪律），从提及该词的方法卡取材合并。
    """
    method_stems = {p.stem.lower() for p in WIKI_METHODS.glob("*.md")}
    counts: Counter = Counter()
    samples: Dict[str, List[str]] = {}
    for p in WIKI_PAPERS.glob("*.md"):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if "已合并" in text[:600]:
            continue
        if _METHOD_CARD_MARK not in text:
            continue
        low = text.lower()
        for term in COMMON_METHOD_TERMS:
            if term.lower() in low:
                counts[term] += 1
                if len(samples.setdefault(term, [])) < 3:
                    samples[term].append(p.stem[:60])

    result = []
    for term, c in counts.most_common():
        if c < min_shared:
            continue
        slug_guess = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", term.lower()).strip("-")
        if term.lower() in method_stems or slug_guess in method_stems:
            continue
        result.append({
            "method": term,
            "card_count": c,
            "sample_papers": samples.get(term, []),
        })
    return result

# 频次 → 优先级提示
def _priority_hint(freq: int) -> str:
    if freq >= 20:
        return "high"
    if freq >= 5:
        return "mid"
    return "low"


def _load_alias_map() -> Dict[str, str]:
    """aliases.json → {别名: 主 stem}。"""
    if not ALIASES_PATH.exists():
        return {}
    try:
        data = json.loads(ALIASES_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}
    amap: Dict[str, str] = {}
    for stem, aliases in data.items():
        items = [aliases] if isinstance(aliases, str) else (aliases or [])
        for a in items:
            if isinstance(a, str):
                amap[a] = stem
    return amap


def scan_dangling_concepts(min_freq: int = 2) -> List[Dict[str, Any]]:
    """扫描全部论文页的悬空 wikilink，返回按频次降序的概念缺口清单。

    悬空定义：[[target]] 的 target 归一化（alias 映射 + 取末段）后
    不在 papers/concepts/methods 任一 stem 集合中，且不匹配课题 ID
    或噪声模式。
    """
    paper_stems = {p.stem for p in WIKI_PAPERS.glob("*.md")}
    concept_stems = {p.stem for p in WIKI_CONCEPTS.glob("*.md")}
    method_stems = {p.stem for p in WIKI_METHODS.glob("*.md")}
    alias_map = _load_alias_map()
    existing = paper_stems | concept_stems | method_stems

    freq = Counter()
    samples: Dict[str, List[str]] = {}
    for p in WIKI_PAPERS.glob("*.md"):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if "已合并" in text[:600]:
            continue
        for m in re.findall(r"\[\[([^\]|#]+)", text):
            target = m.strip()
            if not target or target.startswith("http"):
                continue
            stem = target.split("/")[-1].strip()
            stem = alias_map.get(stem, stem)
            if stem in existing:
                continue
            if _PROPOSAL_ID_RE.match(target) or _PROPOSAL_ID_RE.match(stem):
                continue
            if _NOISE_RE.match(target):
                continue
            # v7.2.16：噪音剔除 + 同义词归一（频次累计到规范名）
            if _is_noise_concept(target) or _is_noise_concept(stem):
                continue
            canon = CONCEPT_SYNONYMS.get(target, CONCEPT_SYNONYMS.get(stem, target))
            if canon in existing:
                continue
            freq[canon] += 1
            if len(samples.setdefault(canon, [])) < 3:
                samples[canon].append(p.stem[:60])

    result = []
    for name, c in freq.most_common():
        if c < min_freq:
            continue
        result.append({
            "name": name,
            "freq": c,
            "priority_hint": _priority_hint(c),
            "sample_sources": samples.get(name, []),
        })
    return result


def _rel_display(path: Path) -> str:
    """显示用相对路径（不可相对化时回退绝对路径，供测试重定向场景）。"""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def emit_concepts_worklist(batch: int = 150) -> int:
    """发射概念撰写工作清单（覆盖式，含 emitted_at 时间戳）。"""
    targets = scan_dangling_concepts(min_freq=2)[:batch]
    save_json(CONCEPTS_WORKLIST, {
        "emitted_at": now_utc(),
        "count": len(targets),
        "consumed_by": "ZCode",
        "task_note": (
            "按清单撰写 knowledge/wiki/concepts/<slug>.md 概念页："
            "含 定义/物理内涵/与林赛研究关联/来源链接 四节；"
            "过 kb_wiki v7.1.3 质量门（正文 ≥200 字 + ≥2 个二级标题 + "
            "≥1 个 [[wikilink]] + tags 非空）；"
            "文件名用英文 slug，frontmatter aliases 含中文名"
        ),
        "targets": targets,
    })
    print(f"  ✓ 概念工作清单: {len(targets)} 项 → {_rel_display(CONCEPTS_WORKLIST)}")
    return len(targets)


def emit_graduate_worklist(min_shared: int = 3) -> int:
    """发射方法页毕业工作清单。"""
    targets = scan_method_graduation(min_shared=min_shared)
    save_json(GRADUATE_WORKLIST, {
        "emitted_at": now_utc(),
        "count": len(targets),
        "consumed_by": "ZCode",
        "task_note": (
            "按清单撰写 knowledge/wiki/methods/<slug>.md 独立方法页："
            "四要素（原理 / 参数表·数值含单位与出处 / 适用边界 / 代表作）"
            "+ 林赛理解节；参数溯源纪律——每个数值给出文献引用；"
            "从 sample_papers 的论文方法卡取材合并"
        ),
        "targets": targets,
    })
    print(f"  ✓ 方法毕业清单: {len(targets)} 项 → {_rel_display(GRADUATE_WORKLIST)}")
    return len(targets)


def _self_check() -> List[str]:
    """自检：小规模真实数据冒烟 + 纯函数行为校验。"""
    msgs: List[str] = []

    # 纯函数校验
    msgs.append("✓ _priority_hint: " + str(
        _priority_hint(30) == "high" and _priority_hint(8) == "mid" and _priority_hint(2) == "low"
    ))
    msgs.append("✓ 课题 ID 排除: " + str(bool(_PROPOSAL_ID_RE.match("general-mos2-20260905"))))
    msgs.append("✓ 噪声排除(年份): " + str(bool(_NOISE_RE.match("2020"))))
    # v7.2.16 净化规则
    msgs.append("✓ 噪音剔除(人名): " + str(
        _is_noise_concept("Corkum") and _is_noise_concept("Krausz")
        and not _is_noise_concept("RABBITT") and not _is_noise_concept("Berry 曲率")))
    msgs.append("✓ 噪音剔除(标题/ID/标签): " + str(
        _is_noise_concept("论文精读：某论文深读")
        and _is_noise_concept("2607.19937")
        and _is_noise_concept("NSFC-强场超快")
        and _is_noise_concept("Edge states and quantum optical high-harmonic generation")))
    msgs.append("✓ 同义词归一: " + str(
        CONCEPT_SYNONYMS["谷电子学"] == "能谷电子学"))

    # 真实库冒烟（存在则扫，不存在跳过）
    if WIKI_PAPERS.exists():
        items = scan_dangling_concepts(min_freq=5)
        msgs.append(f"✓ 悬空扫描冒烟(min_freq=5): {len(items)} 项")
        assert all(i["freq"] >= 5 for i in items)
    else:
        msgs.append("○ wiki/papers 不存在，跳过真实扫描")
    return msgs


def main() -> int:
    parser = argparse.ArgumentParser(description="知识库概念层扩容发射器（零 LLM）")
    parser.add_argument("--scan", action="store_true", help="预览悬空概念频次排行")
    parser.add_argument("--worklist", type=int, nargs="?", const=150, default=0,
                        help="发射概念撰写清单（默认 150 项）")
    parser.add_argument("--graduate", action="store_true",
                        help="方法卡毕业扫描并发射毕业清单")
    parser.add_argument("--min-freq", type=int, default=2, help="悬空最低频次阈值")
    parser.add_argument("--self-check", action="store_true", help="自检")
    args = parser.parse_args()

    if args.self_check:
        for m in _self_check():
            print(m)
        return 0

    if args.scan:
        items = scan_dangling_concepts(min_freq=args.min_freq)
        print(f"悬空概念（频次 ≥{args.min_freq}）: {len(items)} 个")
        for i in items[:40]:
            print(f"  {i['freq']:>4}×  [{i['priority_hint']:<4}]  {i['name'][:60]}")
        return 0

    if args.worklist:
        emit_concepts_worklist(batch=args.worklist)
        return 0

    if args.graduate:
        targets = scan_method_graduation()
        print(f"方法卡毕业候选(≥3 次): {len(targets)} 个")
        for t in targets[:20]:
            print(f"  {t['card_count']:>3}×  {t['method'][:50]}")
        emit_graduate_worklist()
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
