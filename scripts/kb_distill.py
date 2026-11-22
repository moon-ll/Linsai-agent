#!/usr/bin/env python3
"""kb_distill — raw→wiki 批量蒸馏器（v6.9.5）。

背景（2026-08-15 排查结论）：
    health_sensor 持续告警"待蒸馏 raw 积压 508 项"（阈值 300）。
    根因不是任务失败，而是 `distill_raw_to_wiki()` / `save_distilled_wiki()`
    接口自 v3.x 就存在，但**没有任何流水线生产者调用它们**——周末输出端
    做的是归档课题萃取与每日知识萃取，均不覆盖 raw→wiki 蒸馏。接口在、
    编排无，导致 raw/papers 360 篇论文长期零消化。

本模块补上这一环：
    1. 计算 pending 清单（已索引 raw 中无 wiki source_raw 关联者）
    2. 按文件修改时间 FIFO 取最旧 N 篇（--batch，默认 5）
    3. 每篇：生成蒸馏 prompt → llm_gateway（执行类默认链，MiniMax 主，
       额度期自动降级）→ 后处理注入 source_raw frontmatter →
       save_distilled_wiki（门面写入，自动更新图谱/生长日志/索引）
    4. 单篇失败跳过不中断批次；批次结束输出汇总

关键约束：
    - 蒸馏产物必须带 `source_raw` frontmatter——这是 pending_distill
      的判定依据（kb_health.py），缺了它蒸馏了也不减计数。
    - 写入统一走 knowledge_base 门面（v6.8.51 防双 frontmatter 规范）。

用法示例：
    python3 scripts/kb_distill.py --dry-run        # 预览将蒸馏的清单
    python3 scripts/kb_distill.py --batch 5        # 蒸馏最旧 5 篇
    python3 scripts/kb_distill.py --emit-worklist 0  # 发射全量待蒸馏清单（供 ZCode）
    python3 scripts/kb_distill.py --self-check     # 模块自检（零 LLM 调用）

cron 接入（见 setup 提示）：
    每日 12:50（lc-kb-sync 之后）跑一批 5 篇，508 项约 100 天消化；
    蒸馏副产物（wikilinks 注入）同步改善图谱连通性 0.45→阈值上方。

ZCode worklist 双通道（v7.2.28 用户裁决："kb蒸馏加入zcode的worklist"）：
    与方法卡回补（kb_methods_backfill v7.0.7）同模式——LLM cron 批量路径
    保留（gateway 编排继续消化积压），另发射零 LLM 工作清单
    memory/distill-worklist.json 供 ZCode 自动化任务消费。两通道幂等：
    pending 口径以 wiki source_raw 为准，任一通道落盘即减计数。

    ZCode 任务消费方式（库调用，零 LLM 网关）：
        1. 读 worklist 条目：raw_rel（raw 论文文件）、digest_hint
           （fulltext=有全文走五要素精读 / abstract=摘要级轻量笔记）、
           arxiv_id（有全文时可读 knowledge/raw/pdfs/<id>.pdf 或其
           _text_cache 缓存）；
        2. ZCode 会话即模型：读原文按五要素结构撰写笔记正文（直接以
           # 标题开始，frontmatter 由系统补写；数值原样保留含单位，
           摘要级不得编造未给出的数值）；
        3. 落盘：from kb_distill import write_distilled_page
           write_distilled_page("<raw 纯文件名>", body, digest_level)
           ——自动保证 source_raw（纯文件名）+ digest_level frontmatter，
           经 save_distilled_wiki 门面写入（图谱/索引同步），并追加
           方法卡 worklist（source='distill'）。
"""

import argparse
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from common import now_utc  # noqa: E402
from knowledge_base import (  # noqa: E402
    KNOWLEDGE_DIR,
    distill_raw_to_wiki,
    save_distilled_wiki,
)

# v7.2.28 修复：_log 此前被 except 路径引用但从未定义，触发时 NameError
try:
    from logger import get_logger
    _log = get_logger("kb_distill")
except Exception:
    _log = None

DEFAULT_BATCH = 5
MAX_OUTPUT_CHARS = 6000          # 防失控输出
SOURCE_RAW_KEY = "source_raw"    # pending_distill 判定字段
# v6.9.38: 自适应批量档位（--auto）——积压 >300 时 5 篇/天永远追不上
# 日增 40+ 的进料速度（08-22 实测积压 347 且连续 46 次告警不收敛）。
# 升档后单批 LLM 时长约 10-15 分钟（20 篇 × 30-45s/篇），12:50 窗口
# 可承受；回落到 <150 后降回默认档，避免常态多耗 token。
AUTO_BATCH_TIERS = [
    (300, 30),   # v7.1.5: 积压 >300 → 30 篇/天（追赶档，提速 50%）
    (150, 15),   # v7.1.5: 积压 >150 → 15 篇/天（消化档，提速 50%）
]
AUTO_BATCH_FLOOR = DEFAULT_BATCH  # 积压 ≤150 → 5 篇/天（维持档）
# v7.2.75（BUG-36）：单批墙钟预算。hermes cron 对 no-agent 脚本作业的硬超时
# 是 3600s，超时整条作业被判 error（last_status=error + 落 incident）。
# 实测 2026-10-31 18:50 档：30 篇蒸馏（LLM 降级后每篇 60-110s）+ kb_linker
# 补边（1478 条边 × 0.085s/条 + 758 次全量重写 growth-log）合计 >3600s →
# 该档当日零产出（补边写了一半，下次从头再来）。
# 预算留出余量给后置的 kb_linker，剩余篇目留待下一档消化。
DEFAULT_TIME_BUDGET_S = 2400.0  # 40 分钟（cron 硬超时 60 分钟，留 20 分钟给补边）
# 排除目录（相对 KNOWLEDGE_DIR 的 posix 前缀）：
#   raw/pdfs/_text_cache/ 是 PDF 抽取中间缓存（纯数字命名、无语义），
#   蒸馏它们只会产出无意义 wiki 页；kb_health 计数包含它们属上游口径
#   宽松，此处主动排除，避免污染知识库。
EXCLUDE_PREFIXES = ("raw/pdfs/_text_cache/",)
# v6.9.20: 排除自动生成的索引/清单类文件（无原文语义，蒸馏无意义，
# 实测 _pdf-library.md 为 PDF 汇总表，会永久占用 pending 计数）。
EXCLUDE_FILES = ("raw/pdfs/_pdf-library.md",)
# v7.2.75（BUG-35）：排除 raw/projects/ —— 课题库产物不是文献素材。
#
# 背景：raw/projects/{课题id}/ 下是课题的生命周期产物（申请书草稿、评审
# 报告、方法手册、验收报告等），由 feedback_archive / proposal_kb_sync 写入，
# 本就不该被当作「待蒸馏文献」消费。但 pending_distill_list 用
# kb_index.list_raw_files() 全量扫描 raw/，projects/ 未被排除 →
# 367/428（85.8%）的 pending 队列是课题产物。
#
# 三重危害：
#   1. 队列毒化——raw/projects 文件 mtime 普遍更旧（最早 07-26），
#      FIFO「最旧优先」下前 30 名 **100% 是 projects**，真正待蒸馏的
#      raw/papers（61 篇）被永久饿死（实测 papers 最老一篇停在 10-22）。
#   2. 知识污染——课题内部产物被蒸馏成 wiki/concepts/ 页（实测 50 页，
#      含 README / PLAN / INDEX / 立项依据_v0_1 等泛用标题），泛用标题
#      又被 kb_linker 当作「已有 wiki 标题」做全文提及匹配 → PLAN 被
#      162 页正文提及，凭空造出 1478 条 related 边。
#   3. 口径失真——kb_health 的 pending_distill 告警（阈值 300）与
#      health_sensor 的蒸馏积压告警都复用本清单，367 项课题产物计入
#      「文献蒸馏积压」，掩盖真实文献缺口。
#
# 处置：raw/projects/ 不进文献蒸馏队列。课题内容另有 wiki/projects/NSFC-强场超快/
# 镜像与 kb-methods-pack 素材包通道消费（见 proposal_kb_sync.py / kb_methods_pack.py）。
EXCLUDE_DIR_PREFIXES = ("raw/projects/",)
# v7.2.28: ZCode 蒸馏工作清单（零 LLM 发射，ZCode 任务消费）
DISTILL_WORKLIST_PATH = PROJECT_ROOT / "memory" / "distill-worklist.json"


def _is_excluded(rel_path: str) -> bool:
    if rel_path in EXCLUDE_FILES:
        return True
    if any(rel_path.startswith(p) for p in EXCLUDE_PREFIXES):
        return True
    # v7.2.75（BUG-35）：课题产物不进文献蒸馏队列（详见常量处说明）
    if any(rel_path.startswith(p) for p in EXCLUDE_DIR_PREFIXES):
        return True
    return False


# ─────────────────────────────────────────────
# 清单计算
# ─────────────────────────────────────────────

def _wiki_source_raws() -> set:
    """收集现有 wiki 已占用的 source_raw 集合（纯文件名口径）。"""
    from knowledge_base import list_wiki_pages, get_wiki_page
    used = set()
    for pg in list_wiki_pages():
        fm = get_wiki_page(pg.get("path", "")) or {}
        src = (fm.get("frontmatter") or {}).get(SOURCE_RAW_KEY, "")
        if src:
            # 兼容历史数据：source_raw 可能带 raw/papers/ 前缀，统一取纯文件名
            used.add(Path(src).name)
    return used


def pending_distill_list(limit: Optional[int] = None) -> List[Path]:
    """返回待蒸馏 raw 清单（按最旧优先）。

    口径与 kb_health.get_kb_health 的 pending_distill / health_sensor
    告警完全同源：kb_index.list_raw_files() 的 name（纯文件名）对
    wiki frontmatter 的 source_raw（纯文件名）。

    Args:
        limit: 最多返回条数；None 返回全量。

    Returns:
        raw 文件绝对路径列表。
    """
    from kb_index import list_raw_files
    used = _wiki_source_raws()
    files = []
    for f in list_raw_files():
        if Path(f["name"]).name in used or _is_excluded(f["path"]):
            continue
        # v6.9.73: agent 相关性第二道门——被拒（agent_rejected: true）的
        # 论文不进蒸馏队列（保留 raw 作记录，不消耗蒸馏配额）。
        # v6.9.75: 头读窗口 500→8192——kb_importer 的 frontmatter 字段序中
        # agent_rejected 排在 title/authors/agent_note 之后，大协作组论文
        # （30+ 作者）实测偏移 660B+ 即溢出 500B 窗口致过滤器漏检；
        # 8192B 可覆盖 100+ 作者（title 300B + authors 3000B + 摘要前置字段）
        try:
            with (KNOWLEDGE_DIR / f["path"]).open(encoding="utf-8", errors="ignore") as _fh:
                head = _fh.read(8192)
            if re.search(r"agent_rejected:\s*true", head):
                continue
        except OSError:
            pass
        files.append((f["mtime"], KNOWLEDGE_DIR / f["path"]))
    files.sort(key=lambda t: t[0])  # 最旧优先
    out = [p for _, p in files]
    return out[:limit] if limit is not None else out


# ─────────────────────────────────────────────
# 蒸馏执行
# ─────────────────────────────────────────────

def _unwrap_bulleted_frontmatter(llm_output: str) -> str:
    """把被 bullet 包裹的整页文本还原为裸 markdown（v7.2.75）。

    背景（BUG-34）：部分 LLM 把整页（含 YAML frontmatter）包进一个 bullet
    列表项里输出，形如::

        • ---
          title: "X"
          type: concepts
          ---

          # X
          正文…

    `_ensure_source_raw` 只认 `llm_output.lstrip().startswith("---")`，这类
    输出会被判定为「无 frontmatter」→ 再补一块系统头 → 落盘后成为**双块
    frontmatter**（外层系统头 + 正文里 bullet 包裹的真 frontmatter）。
    后果：外层 `tags`/`related` 为空、真实标题/标签被埋进正文，
    `parse_frontmatter` 只读外层 → 元数据全丢；正文开头残留 `• ---`
    噪声；全库已积累 210 页此形态（39 页源自 raw/projects）。

    修法：在补头之前把 bullet 形态还原——去掉行首 bullet 标记与随后的
    统一缩进，**保留**其内层 frontmatter（真实 title/tags/related 都在
    里面，剥掉反而丢元数据），交由 `_ensure_source_raw` 走「有 frontmatter
    → 补 source_raw」正路。

    仅在能明确识别该形态时改写，否则原样返回（fail-open）。
    """
    lines = llm_output.split("\n")
    if not lines:
        return llm_output
    first = lines[0].strip()
    if not re.fullmatch(r"[•\-*]\s*---", first):
        return llm_output
    # 缩进块 = bullet 项内整体缩进的行；取其公共缩进量
    body_lines = lines[1:]
    indents = [len(ln) - len(ln.lstrip()) for ln in body_lines
               if ln.strip()]
    block_indent = min(indents) if indents else 0
    out = ["---"]
    for ln in body_lines:
        if not ln.strip():
            out.append("")
            continue
        cur = len(ln) - len(ln.lstrip())
        if cur >= block_indent:
            out.append(ln[block_indent:])
        else:
            out.append(ln.lstrip())
    return "\n".join(out)


def _ensure_source_raw(llm_output: str, raw_rel: str, wiki_type: str,
                       wiki_name: str) -> str:
    """确保输出含 frontmatter 且带 source_raw（不减计数的关键）。

    - 无 frontmatter → 构造最小合规头（title/type/created/growth_stage）
    - 有 frontmatter → 仅在缺 source_raw 时补写，不覆盖已有字段
    """
    # v6.9.7: created 必须取真实当前时间——此前硬编码 "2026-08-15T00:00:00Z"，
    # 而蒸馏系统提示要求 LLM 只输出正文（构造头部是主路径），导致 lc-kb-distill
    # 每日新蒸馏页的 created 全部冻结在同一天，污染 KB 新鲜度指标与
    # growth_engine 晋升时序判断。
    now = now_utc()
    # v7.2.75（BUG-34）：先剥掉 bullet 包裹形态，否则会被判为「无 frontmatter」
    # 而补出第二块头，落盘成为双 frontmatter（真实元数据被埋在正文里）。
    llm_output = _unwrap_bulleted_frontmatter(llm_output)
    if llm_output.lstrip().startswith("---"):
        if re.search(rf"^{SOURCE_RAW_KEY}\s*:", llm_output, re.M):
            return llm_output
        # 在 frontmatter 结束线前插入
        return re.sub(r"\n---\n", f"\n{SOURCE_RAW_KEY}: \"{raw_rel}\"\n---\n",
                      llm_output, count=1)
    fm = (f"---\ntitle: \"{wiki_name}\"\ntype: {wiki_type}\n"
          f"created: {now}\ngrowth_stage: seedling\n"
          f"{SOURCE_RAW_KEY}: \"{raw_rel}\"\n---\n\n")
    return fm + llm_output




# 五要素深度蒸馏 prompt（v6.9.75 用户校准；v7.0.4 五要素标准收敛至
# literature-reading skill 二节单一真相源，经 _build_deep_distill_prompt
# 注入；此处只保留输出结构契约——代码层只留编排+输出契约的 v7.0 分工）
DEEP_DISTILL_PROMPT = """请基于以下论文【全文】撰写一篇深度研究笔记（林赛，强场超快光学 PI 视角）。

【硬性要求】核心要点必须完整覆盖五要素（标准见 prompt 开头 skill 注入块），每要素一节、各有实质内容；全文数值原样保留（含单位）。
方法密度高的论文（方法创新为核心贡献，或实验/计算细节详尽），"研究方法"节按方法卡格式详述：装置配置、测量序列、关键参数表（数值+单位+出处）、计算设置——这些是课题方案写作的可实施素材；方法密度低则该节从简，不虚构参数。

【结构】输出 markdown（frontmatter 系统补写，直接以 # 标题开始）：
# 标题

## 林赛的理解
（第一人称：这篇工作对我们的研究意味着什么、可以怎么用）

## 研究问题

## 研究背景

## 研究方法

## 主要发现与核心结论

## 潜在研究方向

## 与林赛研究的关联
（具体的实验/理论接口，引用本组方向词：HHG、阿秒、强场驱动、交变磁、莫尔、量子几何等）

## 来源
- 蒸馏自全文（deep-read）
"""


def _build_deep_distill_prompt(raw_md: str, fulltext: str) -> str:
    """构造五要素深度蒸馏 prompt：raw 元数据 + 全文（截断）。

    v7.0.4: 五要素蒸馏标准与通用纪律（数值忠实/挂靠准确）从
    literature-reading skill 二/四节注入（单一真相源），fail-open。
    """
    # skill 标准注入（fail-open：skill 缺失时退回 prompt 内联要求）。
    # v7.0.5 加注五节（方法学整理）——蒸馏的"研究方法"节按方法卡
    # 格式提取装置/序列/参数，为课题方案写作沉淀可实施素材（用户
    # 指示：文献阅读增加专门的方法学整理，方案缺可实施细节的根因
    # 在生产端——方法素材从未系统性进入知识库）。
    _skill_block = ""
    try:
        from skill_loader import inject_block
        _skill_block = inject_block(
            "literature-reading",
            ["二、五要素蒸馏", "五、方法学整理", "四、通用纪律"],
            note="蒸馏硬性标准")
    except Exception:
        pass
    # raw md 的 frontmatter 元数据（标题/作者/年份）供参照
    meta_part = raw_md[:800]
    ft = fulltext[:40000]  # 全文截断（约 1 万 token），覆盖绝大多数论文正文
    return (
        _skill_block
        + "\n" + DEEP_DISTILL_PROMPT
        + "\n\n【论文元数据（frontmatter）】\n" + meta_part
        + "\n\n【论文全文】\n" + ft
        + ("\n\n[全文超长已截断]" if len(fulltext) > 40000 else "")
    )


def _deep_wiki_rel(raw_path: Path) -> str:
    """全文级蒸馏的 wiki 路径（与现有命名规则一致）。"""
    import knowledge_base as _kb
    title_guess = raw_path.stem
    safe_name = _kb._safe_filename(title_guess)
    return f"wiki/papers/{safe_name}.md"


def _is_lite_source(raw_path: Path) -> bool:
    """v7.3.83: 低价值源判定（用户裁决 2026-11-15 token 治理③）。

    简报（weekend collect 的 tier 2）与网页剪藏/手写笔记（tier 3）不做
    五要素精读、输出预算减半（prefer=kb_distill_lite → max_tokens 2048）。
    判定规则：路径含 notes/webclips 段，或文件名带 research_briefing_ /
    daily_memory_ 前缀（简报双命名，与同步口径一致）。
    """
    if any(seg in ("notes", "webclips") for seg in raw_path.parts):
        return True
    return raw_path.name.startswith(("research_briefing_", "daily_memory_"))


def distill_one(raw_path: Path, dry_run: bool = False) -> Dict[str, Any]:
    """蒸馏单篇 raw → wiki。

    Returns:
        {success, raw, wiki, skipped?, error?}
    """
    raw_rel = raw_path.relative_to(KNOWLEDGE_DIR).as_posix()

    # v6.9.75: 分层蒸馏——有全文（deep-read 管线标记 has_fulltext 且
    # _text_cache 命中）走五要素深度蒸馏；否则摘要级轻量笔记。
    raw_text_full = raw_path.read_text(encoding="utf-8", errors="ignore")
    fulltext = None
    if re.search(r"has_fulltext:\s*true", raw_text_full[:1200]):
        m_aid = re.search(r'arxiv_id:\s*"?([\d]{4}\.[\d]{4,5})', raw_text_full)
        if m_aid:
            try:
                from pdf_manager import PdfLibrary
                fulltext = PdfLibrary().get_pdf_text(m_aid.group(1))
            except Exception:
                fulltext = None

    digest_level = "fulltext" if fulltext else "abstract"
    # v7.3.83: 低价值源强制摘要级（简报/剪藏/笔记不做五要素精读）
    lite = _is_lite_source(raw_path)
    if lite and digest_level == "fulltext":
        fulltext = None
        digest_level = "abstract"
    if fulltext:
        prompt = _build_deep_distill_prompt(raw_text_full, fulltext)
        wiki_rel = _deep_wiki_rel(raw_path)
        system = (
            "你是知识库蒸馏器（深度阅读模式）。基于论文全文按五要素结构"
            "撰写研究笔记，直接输出 Markdown 正文（frontmatter 由系统补写），"
            "不要输出解释。五要素必须各有实质内容，定量数据保留原文数值。"
        )
        timeout = 240
    else:
        prepped = distill_raw_to_wiki(raw_rel)
        if not prepped:
            return {"success": False, "raw": raw_rel, "error": "prompt 生成失败"}
        wiki_rel, prompt = prepped
        system = (
            "你是知识库蒸馏器。按用户指令把原始文献提炼为 wiki 页面，"
            "直接输出 Markdown 正文（frontmatter 由系统补写），不要输出解释。"
            "注意：输入仅为摘要级元数据，笔记中不得编造未给出的数值或细节。"
        )
        timeout = 150

    if dry_run:
        return {"success": True, "raw": raw_rel, "wiki": wiki_rel,
                "skipped": True, "digest_level": digest_level,
                **({"lite": True} if lite else {})}

    # v7.3.83: 低价值源走 kb_distill_lite（max_tokens 2048，其余口径同
    # kb_distill）；fulltext 走 kb_distill_deep（16384）。
    prefer_tag = ("kb_distill_deep" if digest_level == "fulltext"
                  else "kb_distill_lite" if lite else "kb_distill")

    from llm_gateway import llm_complete
    # v6.9.15: prefer="kb_distill" → GLM 主模型直连（默认 MiniMax 主链
    # 429 限额期单篇重试+降级最长 369s，350 篇积压不可行）。
    # v6.9.74: glm 对蒸馏长 prompt 104s 失败，改 minimax 优先。
    ok, text, meta = llm_complete(
        system, prompt, timeout=timeout, prefer=prefer_tag,
    )
    # v6.9.75: 空输出重试一次——minimax 推理模型偶发 reasoning tokens
    # 吃满 completion 配额导致正文为空（实测 3/5 概率对长 prompt 触发），
    # 重试一次通常即正常。
    if (not ok or not text or not text.strip()):
        ok, text, meta = llm_complete(
            system, prompt, timeout=timeout, prefer=prefer_tag,
        )
    if not ok or not text or not text.strip():
        return {"success": False, "raw": raw_rel,
                "error": f"LLM 失败: {str(meta.get('error', ''))[:60]}"}
    # v6.9.75: 全文级五要素蒸馏输出预算加倍（6000 字符曾把第五要素截掉）
    out_budget = MAX_OUTPUT_CHARS * 2 if digest_level == "fulltext" else MAX_OUTPUT_CHARS
    if len(text) > out_budget:
        text = text[:out_budget] + "\n\n... [蒸馏输出超长截断]"

    wiki_type = wiki_rel.split("/")[1] if "/" in wiki_rel else "concepts"
    # source_raw 必须是纯文件名——kb_health 以 name 对 name 匹配判定
    # pending_distill，带 raw/ 前缀会导致蒸馏后计数不减。
    final = _ensure_source_raw(text, raw_path.name, wiki_type,
                               Path(wiki_rel).stem)
    # v6.9.75: 标注蒸馏层级（fulltext 五要素精读 / abstract 摘要级）
    # 锚点用 source_raw（kb_distill 产物必有），review_status 不一定存在
    final = re.sub(r'(source_raw:\s*"[^"]*")',
                   rf'\1\ndigest_level: "{digest_level}"', final, count=1)
    save_distilled_wiki(wiki_rel, final, raw_rel)
    # v7.1.0: 蒸馏出口追加方法卡抽取工作清单（用户裁决 2026-09-27：
    # "每日文献阅读也可以增加方法页"——蒸馏完成即追加，让 ZCode 任务在下个
    # 闲时窗口立即为新蒸馏论文补方法卡，不等下一次全量发射）
    wiki_stem = Path(wiki_rel).stem
    try:
        from kb_methods_backfill import append_to_worklist
        append_to_worklist([wiki_stem], source="distill")
    except Exception as exc:
        if _log:
            _log.warning("[kb_distill] 方法卡清单追加失败 %s: %s", wiki_stem, exc)
    return {"success": True, "raw": raw_rel, "wiki": wiki_rel,
            "digest_level": digest_level, **({"lite": True} if lite else {})}


def auto_batch_size(pending_count: int) -> int:
    """v6.9.38: 按积压量返回自适应批量档位。

    Args:
        pending_count: 当前待蒸馏总数。

    Returns:
        该档位下的每日批量（篇）。
    """
    for threshold, batch in AUTO_BATCH_TIERS:
        if pending_count > threshold:
            return batch
    return AUTO_BATCH_FLOOR


def run_batch(batch: int = DEFAULT_BATCH, dry_run: bool = False,
              time_budget_s: float = DEFAULT_TIME_BUDGET_S) -> Dict[str, Any]:
    """执行一批蒸馏。

    Args:
        batch: 本批篇数上限。
        dry_run: 仅预览不调用 LLM。
        time_budget_s: 单批墙钟预算（秒）。超出即停止本批，剩余留待下一档。
            v7.2.75 新增：hermes cron 对脚本的硬超时是 3600s，超时整条
            作业被判 error（实测 2026-10-31 18:50 档：30 篇 LLM + 补边
            共耗时 >3600s → last_status=error → 该档当日零产出且
            补边写了一半，次日从头重来）。加预算后优雅降级为「少做几篇」
            而非「整档失败」。

    Returns:
        {total_pending, attempted, ok, failed, results, stopped_reason?}
    """
    # v6.9.73: 进程级互斥锁——批量蒸馏与 cron 时段（12:50/18:50）可能并发，
    # 无锁时两边会取到同一 pending 重复蒸馏（浪费 LLM 调用）。抢不到锁
    # 温和退出（skipped=lock_busy），与周末流水线语义一致。
    from common import file_lock
    try:
        lock_ctx = file_lock("kb-distill", blocking=False)
        lock = lock_ctx.__enter__()
    except Exception:
        return {"total_pending": len(pending_distill_list()), "attempted": 0,
                "ok": 0, "failed": 0, "results": [], "skipped": "lock_busy"}
    pending = pending_distill_list()
    todo = pending[:batch]
    results = []
    stopped_reason = ""
    started = time.monotonic()
    for f in todo:
        # v7.2.75：预算检查放在每篇之前——已开始的篇跑完，未开始的留到下一档
        if time_budget_s and (time.monotonic() - started) >= time_budget_s:
            stopped_reason = ("time_budget_exhausted: 本批已耗时 %.0fs，"
                              "已达预算 %.0fs，剩余 %d 篇留待下一档"
                              % (time.monotonic() - started, time_budget_s,
                                 len(todo) - len(results)))
            if _log:
                _log.warning("[kb_distill] %s", stopped_reason)
            break
        try:
            results.append(distill_one(f, dry_run=dry_run))
        except Exception as exc:  # 单篇失败不中断批次
            results.append({"success": False,
                            "raw": f.relative_to(KNOWLEDGE_DIR).as_posix(),
                            "error": f"{type(exc).__name__}: {str(exc)[:60]}"})
    ok = sum(1 for r in results if r.get("success"))
    out = {"total_pending": len(pending), "attempted": len(results),
           "ok": ok, "failed": len(results) - ok, "results": results}
    if stopped_reason:
        out["stopped_reason"] = stopped_reason
    return out


# ─────────────────────────────────────────────
# ZCode worklist 双通道（v7.2.28）
# ─────────────────────────────────────────────

def _raw_digest_hint(raw_path: Path) -> Tuple[str, str]:
    """读 raw 头部返回 (digest_hint, arxiv_id)（零 LLM）。

    digest_hint 口径与 distill_one 分层蒸馏一致：frontmatter 标记
    has_fulltext: true 且能提取 arxiv_id → 'fulltext'（五要素精读），
    否则 'abstract'（摘要级轻量笔记）。
    """
    try:
        head = raw_path.read_text(encoding="utf-8", errors="ignore")[:1500]
    except OSError:
        return "abstract", ""
    hint = "fulltext" if re.search(r"has_fulltext:\s*true", head) else "abstract"
    m_aid = re.search(r'arxiv_id:\s*"?([\d]{4}\.[\d]{4,5})', head)
    return hint, (m_aid.group(1) if m_aid else "")


def build_worklist_targets(batch: int = 0) -> List[Dict[str, Any]]:
    """构造待蒸馏工作清单目标（纯计算，零写入、零 LLM）。

    Args:
        batch: 最多返回条数；0 表示全量。

    Returns:
        目标列表：raw_name / raw_rel / digest_hint / arxiv_id / mtime，
        按 pending_distill_list 的最旧优先序。
    """
    from datetime import datetime, timezone
    targets: List[Dict[str, Any]] = []
    for p in pending_distill_list():
        hint, aid = _raw_digest_hint(p)
        targets.append({
            "raw_name": p.name,
            "raw_rel": p.relative_to(KNOWLEDGE_DIR).as_posix(),
            "digest_hint": hint,
            "arxiv_id": aid,
            "mtime": datetime.fromtimestamp(
                p.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        })
        if batch and len(targets) >= batch:
            break
    return targets


def emit_worklist(batch: int = 0) -> Dict[str, Any]:
    """发射待蒸馏工作清单（零 LLM，供 ZCode 自动化任务消费）。

    全量覆盖式发射（与方法卡 worklist 语义一致：ZCode 按出现顺序消费，
    重新发射即刷新清单；已蒸馏页因 pending 口径自动出队）。
    """
    from common import save_json
    targets = build_worklist_targets(batch=batch)
    save_json(DISTILL_WORKLIST_PATH, {
        "emitted_at": now_utc(),
        "count": len(targets),
        "total_pending": len(pending_distill_list()),
        "targets": targets,
    })
    print(f"  ✓ 蒸馏工作清单: {len(targets)} 篇 → "
          f"{DISTILL_WORKLIST_PATH.relative_to(PROJECT_ROOT)}")
    for t in targets[:6]:
        print(f"    [{t['digest_hint']}] {t['raw_name'][:55]}")
    if len(targets) > 6:
        print(f"    …共 {len(targets)} 篇")
    return {"count": len(targets)}


def _compose_distilled_page(body: str, raw_name: str,
                            digest_level: str) -> str:
    """ZCode 蒸馏正文 → 合规 wiki 页文本（纯函数，零写入）。

    保证：frontmatter 存在、source_raw 为纯文件名（pending 减计数
    的判定字段）、digest_level 标注（与 distill_one LLM 路径同契约）。
    """
    final = _ensure_source_raw(body, raw_name, "papers", Path(raw_name).stem)
    if 'digest_level:' not in final:
        final = re.sub(r'(source_raw:\s*"[^"]*")',
                       rf'\1\ndigest_level: "{digest_level}"', final, count=1)
    return final


def write_distilled_page(raw_name: str, body: str,
                         digest_level: str = "abstract") -> Dict[str, Any]:
    """ZCode 蒸馏落盘工具（库调用，零 LLM 网关）。

    ZCode 任务读 raw 原文（+可选全文 PDF/_text_cache）按五要素结构撰写
    正文后调本函数落盘——与 LLM cron 路径同一出口契约：
        - source_raw 纯文件名 frontmatter（pending_distill 减计数）
        - digest_level 标注（fulltext 五要素精读 / abstract 摘要级）
        - save_distilled_wiki 门面写入（图谱/生长日志/索引同步）
        - 追加方法卡 worklist（source='distill'，fail-open）

    Returns:
        {success, raw, wiki, digest_level?, error?}
    """
    raw_path = KNOWLEDGE_DIR / "raw" / "papers" / raw_name
    if not raw_path.exists():
        # 兜底：按纯文件名在 pending 清单反查（raw 可能不在 papers/ 直下）
        raw_path = next((p for p in pending_distill_list()
                         if p.name == raw_name), None)
    if not raw_path or not raw_path.exists():
        return {"success": False, "raw": raw_name,
                "error": "raw 文件不存在（已蒸馏或未入库）"}
    if not body or not body.strip():
        return {"success": False, "raw": raw_name, "error": "正文为空"}

    raw_rel = raw_path.relative_to(KNOWLEDGE_DIR).as_posix()
    wiki_rel = _deep_wiki_rel(raw_path)
    final = _compose_distilled_page(body, raw_name, digest_level)
    save_distilled_wiki(wiki_rel, final, raw_rel)
    # 蒸馏出口追加方法卡抽取清单（与 distill_one 同钩子，fail-open）
    try:
        from kb_methods_backfill import append_to_worklist
        append_to_worklist([Path(wiki_rel).stem], source="distill")
    except Exception as exc:
        if _log:
            _log.warning("[kb_distill] ZCode 落盘方法卡清单追加失败 %s: %s",
                         raw_name, exc)
    return {"success": True, "raw": raw_rel, "wiki": wiki_rel,
            "digest_level": digest_level}


# ─────────────────────────────────────────────
# CLI / 自检
# ─────────────────────────────────────────────

def _self_check() -> bool:
    """模块自检：清单计算 + frontmatter 注入逻辑（零 LLM、零写入）。"""
    ok = True
    # 1) 清单类型与排序
    lst = pending_distill_list(limit=3)
    if not isinstance(lst, list):
        print("✗ pending_distill_list 返回类型错误")
        ok = False
    else:
        print(f"✓ pending 清单（抽样 {len(lst)} 条，类型正确）")

    # 2) frontmatter 注入：无头 → 构造
    no_fm = _ensure_source_raw("正文内容", "x.md", "papers", "x")
    if no_fm.startswith("---") and 'source_raw: "x.md"' in no_fm:
        print("✓ 无 frontmatter → 构造含 source_raw（纯文件名）")
    else:
        print("✗ 无 frontmatter 构造失败"); ok = False

    # 3) frontmatter 注入：有头缺字段 → 补写
    has_fm = "---\ntitle: y\ntype: papers\n---\n\n正文"
    fixed = _ensure_source_raw(has_fm, "y.md", "papers", "y")
    if 'source_raw: "y.md"' in fixed and fixed.count("---") == 2:
        print("✓ 有 frontmatter 缺字段 → 补写 source_raw（纯文件名）")
    else:
        print("✗ 补写失败"); ok = False

    # 4) 已有字段 → 不覆盖
    keep = "---\nsource_raw: \"z.md\"\ntype: papers\n---\n\n正文"
    kept = _ensure_source_raw(keep, "other.md", "papers", "z")
    if 'z.md' in kept and 'other.md' not in kept:
        print("✓ 已有 source_raw → 不覆盖")
    else:
        print("✗ 覆盖了已有字段"); ok = False

    # 5) 排除规则（v6.9.20 回归：索引清单文件不入待蒸馏）
    if _is_excluded("raw/pdfs/_pdf-library.md") and \
            _is_excluded("raw/pdfs/_text_cache/123.md") and \
            not _is_excluded("raw/papers/2024-x.md"):
        print("✓ 排除规则：索引清单/_text_cache 排除，正常论文保留")
    else:
        print("✗ 排除规则失效"); ok = False

    # 6) created 时间戳非冻结（v6.9.7 回归：与当前时间差 < 24h）
    import re as _re
    from datetime import datetime, timezone, timedelta
    fresh = _ensure_source_raw("正文内容", "x.md", "papers", "x")
    m = _re.search(r'^created:\s*"?(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)"?', fresh, _re.M)
    if m:
        try:
            ts = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            age = datetime.now(timezone.utc) - ts
            if abs(age) < timedelta(hours=24):
                print("✓ 构造头 created 取真实当前时间（非冻结）")
            else:
                print(f"✗ created 冻结在 {m.group(1)}"); ok = False
        except ValueError:
            print(f"✗ created 格式不可解析: {m.group(1)}"); ok = False
    else:
        print("✗ 构造头缺失 created 字段"); ok = False

    # 7) ZCode 落盘正文合成（v7.2.28）：source_raw 纯文件名 + digest_level
    composed = _compose_distilled_page("# 标题\n\n## 林赛的理解\n正文。",
                                       "2019-1911.12092-x.md", "fulltext")
    if ('source_raw: "2019-1911.12092-x.md"' in composed
            and 'digest_level: "fulltext"' in composed):
        print("✓ ZCode 落盘合成：source_raw 纯文件名 + digest_level 注入")
    else:
        print("✗ ZCode 落盘合成失败"); ok = False

    # 8) digest_level 已有时不重复注入
    pre = "---\nsource_raw: \"a.md\"\ndigest_level: \"abstract\"\ntype: papers\n---\n\n正文"
    composed2 = _compose_distilled_page(pre, "a.md", "abstract")
    if composed2.count("digest_level:") == 1:
        print("✓ digest_level 已存在 → 不重复注入")
    else:
        print("✗ digest_level 重复注入"); ok = False

    # 9) 工作清单目标构造（纯计算零写入）：batch 截断 + 字段齐备
    targets = build_worklist_targets(batch=2)
    if (len(targets) <= 2
            and all(("raw_name" in t and "digest_hint" in t
                     and "arxiv_id" in t and "raw_rel" in t) for t in targets)):
        print(f"✓ 工作清单目标构造（抽样 {len(targets)} 条，字段齐备）")
    else:
        print("✗ 工作清单目标构造异常"); ok = False

    print("自检结果:", "✓ 通过" if ok else "✗ 失败")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description="raw→wiki 批量蒸馏器")
    ap.add_argument("--batch", type=int, default=DEFAULT_BATCH,
                    help=f"本批蒸馏篇数（默认 {DEFAULT_BATCH}）")
    ap.add_argument("--auto", action="store_true",
                    help="v6.9.38: 按积压量自适应批量（>300→20 篇，>150→10 篇，否则 5 篇）")
    ap.add_argument("--dry-run", action="store_true", help="仅预览不调用 LLM")
    ap.add_argument("--time-budget", type=float, default=DEFAULT_TIME_BUDGET_S,
                    metavar="SEC",
                    help=f"v7.2.75: 单批墙钟预算秒数（默认 {DEFAULT_TIME_BUDGET_S:.0f}，"
                         f"0 表示不限；超出即停批，剩余留待下一档）")
    ap.add_argument("--emit-worklist", type=int, default=None, metavar="N",
                    help="v7.2.28: 发射待蒸馏工作清单供 ZCode 消费（N=0 全量，零 LLM）")
    ap.add_argument("--self-check", action="store_true", help="模块自检")
    args = ap.parse_args()

    if args.self_check:
        return 0 if _self_check() else 1

    if args.emit_worklist is not None:
        r = emit_worklist(batch=args.emit_worklist)
        return 0 if r["count"] >= 0 else 1

    batch = args.batch
    if args.auto:
        # 先取清单定档位再执行（run_batch 内部会重新取一次，开销可忽略：
        # 清单计算为纯文件系统遍历，无 LLM）
        pending_count = len(pending_distill_list())
        batch = auto_batch_size(pending_count)
        print(f"自适应批量: 积压 {pending_count} → 本批 {batch} 篇")

    r = run_batch(batch=batch, dry_run=args.dry_run,
                  time_budget_s=args.time_budget)
    print(f"待蒸馏总量: {r['total_pending']}（阈值 300）")
    print(f"本批: {r['attempted']} 篇，✓ {r['ok']}，✗ {r['failed']}")
    if r.get("stopped_reason"):
        print(f"⚠ {r['stopped_reason']}")
    for item in r["results"]:
        mark = "○ 预览" if item.get("skipped") else ("✓" if item["success"] else "✗")
        extra = f" → {item.get('wiki', '')}" if item.get("wiki") else \
                f" | {str(item.get('error', ''))[:70]}"
        print(f"  {mark} {item['raw']}{extra}")
    return 0 if (r["failed"] == 0 or args.dry_run) else 1


if __name__ == "__main__":
    sys.exit(main())
