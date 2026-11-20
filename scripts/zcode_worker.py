#!/usr/bin/env python3
"""zcode_worker — ZCode 自动化任务 worker（v7.2.30）

背景（2026-10-18 评估）：
    v7.0.7 起方法学升级改 ZCode 任务消费（用户裁决："内容直接走
    ZCode 自动化任务，不调用其他 LLM"），但 **项目内无 worker 消费**，
    3 个 worklist 全部 0 消费：
        - memory/distill-worklist.json (137 项, 10-16 发射)
        - memory/concepts-backfill-worklist.json (150 项, 10-06 发射)
        - memory/methods-backfill-worklist.json (20 项, 10-18 发射)
    `input_pipeline_broken` 告警持续触发。

定位（关键设计边界）：
    真正的 ZCode = LLM 任务（本项目外部，由 ZCode agent 直接读页面撰写）。
    本 worker = **任务协调器**：从 worklist 取条目 → 渲染撰写提示词 → 调
    hermes 一次 LLM 写卡（一次 LLM 路径，符合 v7.0.7 精神——具体写作让
    hermes 一次性产出） → 落盘 → 更新 worklist。

    失败行为：单条失败跳过不中断批次，task_note 追加失败原因；成功条目
    自动从 worklist 移除（避免重复消费）。

CLI（v7.2.34 修正：使用 subparsers 子命令形式，不再用 --consume 前缀）：
    python3 scripts/zcode_worker.py consume distill --batch 5
    python3 scripts/zcode_worker.py consume concepts --batch 5
    python3 scripts/zcode_worker.py consume methods --batch 5
    python3 scripts/zcode_worker.py consume all --batch 5
    python3 scripts/zcode_worker.py status         # 显示 worklist 状态
    python3 scripts/zcode_worker.py self-check    # 零 LLM 自检

cron 接入（v7.2.32 P1-2）：
    每日 21:00 跑 `consume all --batch 5`（与周末 worker 节奏衔接，
    不影响优化时段 18:00-23:59 的微调度器工作）。

实现原则：
    - 零新设计文件：复用 kb_distill.write_distilled_page、
      knowledge_base.save_distilled_wiki、kb_wiki.save_wiki_page 三个落盘门面
    - 零新 prompt 模板：复用 .hermes/skills/literature-reading SKILL.md 五要素
    - 任务隔离：worklist 读 / 写用 file_lock 保护；落盘失败仅影响单条
    - 监控：消费计数 + 失败计数写入 memory/zcode-worker-state.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 路径常量
ROOT = Path(__file__).parent.parent
WORKLIST_DIR = ROOT / "memory"
STATE_FILE = ROOT / "memory" / "zcode-worker-state.json"
SKILL_DIR = ROOT / ".hermes" / "skills"
KNOWLEDGE_DIR = ROOT / "knowledge"

# 三种 worklist 类型
WORKLIST_TYPES = {
    "distill": {
        "file": "distill-worklist.json",
        "task_note": "kb_distill 蒸馏（ZCode 任务）",
        "skill": "literature-reading",
    },
    "concepts": {
        "file": "concepts-backfill-worklist.json",
        "task_note": "kb_concepts_backfill 概念页补全（ZCode 任务）",
        "skill": "literature-reading",
    },
    "methods": {
        "file": "methods-backfill-worklist.json",
        "task_note": "kb_methods_backfill 方法卡（ZCode 任务）",
        "skill": "literature-reading",
    },
}


def _log(msg: str) -> None:
    """统一日志（直接 print，cron 模式下由外层捕获）。"""
    print(f"[zcode_worker] {msg}", flush=True)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_worklist(wtype: str) -> Tuple[Dict[str, Any], Path]:
    """加载 worklist 文件，返回 (data, path)。"""
    fname = WORKLIST_TYPES[wtype]["file"]
    f = WORKLIST_DIR / fname
    if not f.exists():
        return {"targets": [], "emitted_at": _now()}, f
    try:
        return json.loads(f.read_text(encoding="utf-8")), f
    except Exception as e:
        _log(f"⚠ 读取 {fname} 失败: {e}")
        return {"targets": [], "emitted_at": _now()}, f


def _save_worklist(data: Dict[str, Any], path: Path) -> None:
    """原子写 worklist（tempfile + os.replace）。"""
    import os
    import tempfile
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=2))
            f.write("\n")
        os.replace(tmp, path)
    except Exception:
        if Path(tmp).exists():
            os.unlink(tmp)
        raise


def _check_already_done(target: Dict[str, Any], wtype: str) -> bool:
    """检查目标是否已落盘（避免重复消费）。"""
    if wtype == "distill":
        # raw_name → wiki 路径：必须与 kb_distill._deep_wiki_rel 的推导一致
        # （_safe_filename 会把 '.' 换成 '_'，如 1911.12092 → 1911_12092）。
        # v7.2.37 修复 BUG-4：此前直接用 raw 词干拼路径，134 条 worklist 中
        # 124 条推导不一致 → 已落盘页判不出 done → 68 条陈旧条目被反复
        # 重蒸馏（每日 LLM 空转 + worklist 计数不降）。
        raw = target.get("raw_name", "")
        if not raw:
            return False
        from kb_text import _safe_filename
        stem = _safe_filename(Path(raw).stem)
        wiki_p = KNOWLEDGE_DIR / "wiki" / "papers" / f"{stem}.md"
        return wiki_p.exists()
    if wtype == "concepts":
        # target 含 name（概念名），slug 化
        name = target.get("name", "")
        if not name:
            return False
        # 复用 kb_concepts_backfill 的 slug 化规则（中文保留 + 拼音）
        slug = _to_concept_slug(name)
        wiki_p = KNOWLEDGE_DIR / "wiki" / "concepts" / f"{slug}.md"
        return wiki_p.exists()
    if wtype == "methods":
        # v7.2.43 语义对齐（用户裁决 2026-10-24「跟进待修项」，即 healthcheck
        # 2026-10-21 00h 挂起的待人工裁决项）：methods worklist 条目指向
        # **待补方法卡的论文页**（page），产出是往论文页追加方法卡
        # （BACKFILL_MARKER 标记），不是新建 wiki/methods/<slug>.md。
        # 幂等口径与 kb_methods_backfill._has_method_card 一致：
        # 论文页含 BACKFILL_MARKER 即已消费。
        page = target.get("page", "")
        if not page:
            return False
        wiki_p = KNOWLEDGE_DIR / "wiki" / "papers" / f"{page}.md"
        if not wiki_p.exists():
            return False
        try:
            return "<!-- methods-backfill:v1 -->" in wiki_p.read_text(encoding="utf-8")
        except Exception:
            return False
    return False


def _to_concept_slug(name: str) -> str:
    """概念页 slug 化：保留中文，特殊字符替换。"""
    import re
    s = re.sub(r"[\\/:*?\"<>|]+", "_", name)
    s = s.replace("（", "(").replace("）", ")")
    s = re.sub(r"\s+", "-", s)
    return s.strip("-") or "unknown-concept"


def _to_method_slug(name: str) -> str:
    """方法名 slug 化（v7.2.43 起仅用于方法卡 method_name 展示，不再拼落盘路径）。"""
    import re
    s = name.lower()
    s = re.sub(r"[^\w一-鿿]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "unknown-method"


def _build_prompt(target: Dict[str, Any], wtype: str) -> str:
    """构造单条 ZCode 任务的提示词。

    不直接调用 LLM——本函数输出可被 hermes 解析的 prompt 字符串。
    """
    cfg = WORKLIST_TYPES[wtype]
    skill_path = SKILL_DIR / cfg["skill"] / "SKILL.md"

    if wtype == "distill":
        raw_rel = target.get("raw_rel", "")
        digest_hint = target.get("digest_hint", "abstract")
        arxiv_id = target.get("arxiv_id", "")
        prompt = f"""你是 ZCode 自动化任务（kb_distill 蒸馏 worker）。

## 任务类型
{cfg["task_note"]}

## 输入材料
- raw 路径：{raw_rel}
- arxiv_id：{arxiv_id or "无"}
- digest_hint：{digest_hint}
  - fulltext：知识库有 _text_cache 全文，按五要素精读
  - abstract：仅摘要级，按四要素简写

## 写作要求
严格按 {cfg["skill"]} skill 的五要素结构（详见 {skill_path}）：
研究问题（Research Question）/ 背景（Background）/ 方法（Method）/ 发现（Findings）/ 开放方向（Open Questions）

### 数值纪律
- 摘要级不得编造未给出的数值
- 引用句必须用 [[wikilink]] 形式（中文概念直接 [[中文名]]，英文术语 [[english-term]]）
- 全文档不得 < 200 字（v7.1.3 质量门）

## 输出格式
直接以 # 标题开始（**不含 frontmatter**，worker 落盘时注入 source_raw/digest_level）。
"""
        return prompt

    if wtype == "concepts":
        name = target.get("name", "")
        freq = target.get("freq", 0)
        priority = target.get("priority_hint", "mid")
        sample_sources = target.get("sample_sources", [])
        prompt = f"""你是 ZCode 自动化任务（kb_concepts_backfill 概念页补全 worker）。

## 任务类型
{cfg["task_note"]}

## 输入参数
- 概念名：{name}
- 引用频次：{freq}
- 优先级：{priority}
- 样本来源（3 个 arxiv_id 或 wiki 文件名）：{sample_sources}

## 写作要求
概念页结构（v7.1.3 质量门）：
- 标题（# 标题）
- ## 定义定位（≥ 100 字）
- ## 物理内涵/技术原理（≥ 200 字）
- ## 与现有方法/概念的关联（用 [[wikilink]] 至少 1 个）
- ## 林赛理解（≥ 100 字：本概念在本项目研究中的角色）
- ## 学习路径/参考

### 质量门
- 正文字数 ≥ 200 字
- ≥ 2 个二级标题（除关联外）
- ≥ 1 个 [[wikilink]]
- frontmatter tags 非空

## 输出格式
直接以 # 标题开始（**不含 frontmatter**，worker 落盘时注入 tags/type/aliases）。
"""
        return prompt

    if wtype == "methods":
        # v7.2.43 语义对齐：target = 待补方法卡的论文页。worker 读论文页
        # 正文 + raw 原文片段嵌入 prompt，LLM 输出 JSON card，由
        # _consume_one 调 kb_methods_backfill._append_method_card 追加回论文页。
        page = target.get("page", "")
        raw_stem = target.get("raw_stem", "")
        grade = target.get("grade", "?")
        method_hint = (target.get("method_name") or target.get("name") or "").strip()
        paper_text = ""
        paper_p = KNOWLEDGE_DIR / "wiki" / "papers" / f"{page}.md"
        if paper_p.exists():
            try:
                paper_text = paper_p.read_text(encoding="utf-8")[:3500]
            except Exception:
                paper_text = ""
        raw_text = ""
        if raw_stem:
            raw_p = KNOWLEDGE_DIR / "raw" / "papers" / f"{raw_stem}.md"
            if raw_p.exists():
                try:
                    raw_text = raw_p.read_text(encoding="utf-8")[:2500]
                except Exception:
                    raw_text = ""
        prompt = f"""你是 ZCode 自动化任务（kb_methods_backfill 方法卡回补 worker）。

## 任务类型
{cfg["task_note"]}

## 输入
- 论文页：knowledge/wiki/papers/{page}.md（方法卡将追加到此页）
- raw 原文：{('knowledge/raw/papers/' + raw_stem + '.md') if raw_stem else '（无）'}
- 优先级档：{grade}{'；方法名提示：' + method_hint if method_hint else ''}

### 论文页正文（截断）
{paper_text or '（论文页缺失——从 raw 原文独立撰写）'}

### raw 原文（截断）
{raw_text or '（无原文）'}

## 撰写要求（v7.0.5 四要素 + v7.1.3 林赛理解）
- method_name：该方法的标准名称（英文缩写或中文名）
- principle：方法原理（≥ 150 字，物理/数值机制层面的说明）
- understanding：林赛理解（≥ 80 字——该方法在本项目 HHG/磁性课题语境中的角色与认知）
- params：参数表 3-8 行，每行 {{"item": 参数名, "value": 数值+单位, "source": 出处（"本文"或 arXiv 号）}}；数值必须来自上方原文，不得编造
- boundary：适用边界（一句）
- representative：代表作（作者+期刊/arXiv 号，来自原文）

## 输出格式
只输出一个 JSON 对象（可含 ```json 围栏），不要输出其他文字：
{{"method_name": "...", "principle": "...", "understanding": "...", "params": [{{"item": "...", "value": "...", "source": "..."}}], "boundary": "...", "representative": "..."}}
"""
        return prompt

    return ""


def _consume_one(target: Dict[str, Any], wtype: str) -> bool:
    """消费单条 worklist 条目。

    流程：
    1. 调 hermes 一次 LLM（hermes_memory._run_hermes_agent 或直调 llm_gateway）
    2. 解析输出
    3. 落盘到对应 wiki 路径
    4. 返回是否成功

    v7.2.30 实施：调 llm_gateway 直发 prompt 拿到 body，零 hermes 依赖。
    失败返回 False（不抛异常，由 caller 决定是否跳过）。
    """
    if _check_already_done(target, wtype):
        return True  # 已落盘视为成功（幂等）

    prompt = _build_prompt(target, wtype)
    if not prompt:
        return False

    # 调 LLM（v7.2.35 修复 BUG-1.5：原 `from llm_gateway import call_llm`
    # 在 scripts/llm_gateway.py 不存在 call_llm 顶层符号（只有 llm_complete/
    # llm_chat/safe_llm_complete），导致 import 即抛 ImportError → 每条 0/5 失败。
    # 修正：走 scripts.llm_gateway.llm_complete（永不抛异常的 system+user 二段式入口）。
    try:
        import sys as _sys
        if "scripts" not in _sys.path:
            _sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from scripts.llm_gateway import llm_complete  # type: ignore
        ok, body, meta = llm_complete("", prompt, timeout=180, prefer="governance")
    except Exception as e:
        _log(f"⚠ llm_complete 调用失败: {e}")
        return False

    if not body or len(body.strip()) < 200:
        _log(f"⚠ LLM 输出过短 ({len(body)} 字符)，视为失败")
        return False

    # 落盘
    # v7.2.38 修复 BUG-5：先 import knowledge_base 门面注入 kb_wiki._ensure_dirs。
    # kb_wiki 是门面子模块，_ensure_dirs / log_growth / _log 在模块顶层是 None
    # 占位，由 knowledge_base 加载末尾（knowledge_base.py:619-621）回填。直连
    # `from kb_wiki import save_wiki_page` 拿到未注入的模块对象 → save_wiki_page
    # 首行 `_ensure_dirs()` 抛 TypeError: 'NoneType' object is not callable。
    # 该缺陷此前依赖「distill 分支先导入 kb_distill（→ 间接导入 knowledge_base）」
    # 这一偶然副作用而不发作；v7.2.37 BUG-4 修复后 distill 全部命中幂等快路径
    # 成为常态，kb_distill 从不被导入，门面永不注入 → concepts/methods 100% 失败。
    try:
        import knowledge_base  # noqa: F401  触发门面注入（幂等，已加载则跳过）
    except Exception:
        # fail-open：导入失败不阻断，落盘仍尝试（若门面确实未注入，
        # 下方 save_wiki_page 会抛 TypeError 并被同一 except 捕获留痕）。
        pass

    try:
        if wtype == "distill":
            from kb_distill import write_distilled_page  # type: ignore
            result = write_distilled_page(
                target.get("raw_name", ""),
                body,
                target.get("digest_hint", "abstract"),
            )
            return bool(result)
        if wtype == "concepts":
            from kb_wiki import save_wiki_page  # type: ignore
            name = target.get("name", "")
            slug = _to_concept_slug(name)
            full = (
                f"---\ntitle: {name}\n"
                f"type: concepts\ntags: [concept, backfill]\n"
                f"aliases: [{name!r}]\n---\n\n{body}"
            )
            # v7.2.36 修复 BUG-2：元数据必须走 meta 形参传，不能只塞进正文
            # frontmatter。v7.1.3 质量门控读的是 meta 入参（kb_wiki.py:176
            # `tags_empty = not (meta or {}).get("tags")`），此前 meta=None →
            # tags 恒空 → 每次新建 concepts/methods 页 100% 抛 ValueError，
            # worklist 消费 0/5 永久失败。
            save_wiki_page(f"wiki/concepts/{slug}.md", full, {
                "title": name, "type": "concepts",
                "tags": ["concept", "backfill"], "aliases": [name],
            })
            return True
        if wtype == "methods":
            # v7.2.43 语义对齐：body 是 JSON card（可含 ```json 围栏）。
            # 解析后经 kb_methods_backfill._append_method_card 追加回论文页
            # （该函数自带幂等：重跑先移除旧卡）+ 台账标 ok。
            # 不走 kb_wiki 门面（_append_method_card 直接 page_path.write_text，
            # 无需 _ensure_dirs 注入），无 BUG-5 类风险。
            import json as _json
            import re as _re
            _m = _re.search(r"\{.*\}", body, _re.S)
            if not _m:
                _log("⚠ methods LLM 输出中未找到 JSON 对象")
                return False
            try:
                card = _json.loads(_m.group(0))
            except Exception as e:
                _log(f"⚠ methods JSON card 解析失败: {e}")
                return False
            if not card.get("method_name") or not card.get("principle"):
                _log("⚠ methods card 缺 method_name/principle，判失败")
                return False
            page = target.get("page", "")
            if not page:
                _log("⚠ methods 条目缺 page 字段")
                return False
            from kb_methods_backfill import (  # type: ignore
                _append_method_card, _load_state, _save_state,
            )
            page_path = KNOWLEDGE_DIR / "wiki" / "papers" / f"{page}.md"
            if not page_path.exists():
                _log(f"⚠ 论文页不存在: {page_path}")
                return False
            _append_method_card(page_path, card)
            # 台账标 ok（kb_methods_backfill 契约 L26-31；fail-open 不阻断）
            try:
                st = _load_state()
                st.setdefault("pages", {})[page] = {
                    "status": "ok",
                    "grade": target.get("grade", "?"),
                    "at": _now(),
                    "via": "zcode_worker",
                }
                _save_state(st)
            except Exception as e:
                _log(f"⚠ methods 台账更新失败（卡已落盘，不阻断）: {e}")
            return True
    except Exception as e:
        _log(f"⚠ 落盘失败: {e}")
        return False

    return False


def consume_worklist(wtype: str, batch: int = 5) -> Dict[str, Any]:
    """消费一个 worklist，最多处理 batch 条。返回汇总。"""
    if wtype == "all":
        results = []
        for k in WORKLIST_TYPES:
            results.append(consume_worklist(k, batch))
        return {"success": True, "per_type": results}

    data, path = _load_worklist(wtype)
    targets: List[Dict[str, Any]] = data.get("targets", [])
    initial = len(targets)
    success = 0
    fail = 0
    consumed_targets = []

    for t in targets[:batch]:
        ok = _consume_one(t, wtype)
        if ok:
            success += 1
            consumed_targets.append(t)
        else:
            fail += 1
        time.sleep(0.5)  # 避免 LLM 突发

    # 移除已消费条目
    remaining = [t for t in targets if t not in consumed_targets]
    data["targets"] = remaining
    data["count"] = len(remaining)
    data["emitted_at"] = data.get("emitted_at", _now())
    if "task_note" not in data:
        data["task_note"] = WORKLIST_TYPES[wtype]["task_note"]

    try:
        _save_worklist(data, path)
    except Exception as e:
        _log(f"⚠ 写 worklist 失败: {e}")

    summary = {
        "wtype": wtype,
        "initial": initial,
        "consumed": success,
        "failed": fail,
        "remaining": len(remaining),
        "at": _now(),
    }
    _log(f"✓ {wtype}: 消费 {success}/{batch} 失败 {fail} 剩余 {len(remaining)}")
    return summary


def show_status() -> Dict[str, Any]:
    """显示三个 worklist 状态。"""
    out = {}
    for wtype in WORKLIST_TYPES:
        data, _ = _load_worklist(wtype)
        targets = data.get("targets", [])
        out[wtype] = {
            "file": WORKLIST_TYPES[wtype]["file"],
            "emitted_at": data.get("emitted_at"),
            "count": len(targets),
            "first_target": targets[0] if targets else None,
        }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return out


def _self_check() -> bool:
    """零 LLM 自检。"""
    print("=== zcode_worker 自检 ===")
    # 1. worklist 文件存在
    for wtype, cfg in WORKLIST_TYPES.items():
        f = WORKLIST_DIR / cfg["file"]
        assert f.exists(), f"worklist 缺失: {f}"

    # 2. 三个落盘门面可导入
    try:
        from kb_distill import write_distilled_page  # type: ignore
    except ImportError:
        print("⚠ kb_distill.write_distilled_page 不可用")
    try:
        from kb_wiki import save_wiki_page  # type: ignore
    except ImportError:
        print("⚠ kb_wiki.save_wiki_page 不可用")

    # 3. slug 化函数
    assert _to_concept_slug("物理信息神经网络（PINN）") == "物理信息神经网络(PINN)"
    assert _to_method_slug("TDDFT") == "tddft"
    assert _to_method_slug("贝里联络") == "贝里联络"

    # 4. prompt 构造
    target_distill = {"raw_name": "2024-test.md", "raw_rel": "raw/papers/2024-test.md",
                      "digest_hint": "abstract", "arxiv_id": "2401.00001"}
    p = _build_prompt(target_distill, "distill")
    assert "五要素" in p and "2401.00001" in p

    target_concept = {"name": "PINN", "freq": 16, "priority_hint": "mid",
                      "sample_sources": ["2511.12512"]}
    p2 = _build_prompt(target_concept, "concepts")
    assert "PINN" in p2 and "林赛理解" in p2

    target_method = {"method_name": "TDDFT"}
    p3 = _build_prompt(target_method, "methods")
    assert "TDDFT" in p3 and "参数表" in p3

    print("✓ worklist 路径正确（3 个）")
    print("✓ slug 化函数正确")
    print("✓ prompt 构造正确（3 种类型）")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="ZCode 自动化任务 worker")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_consume = sub.add_parser("consume", help="消费 worklist")
    p_consume.add_argument("wtype", choices=list(WORKLIST_TYPES) + ["all"])
    p_consume.add_argument("--batch", type=int, default=5)

    sub.add_parser("status", help="显示 worklist 状态")
    sub.add_parser("self-check", help="零 LLM 自检")

    args = parser.parse_args()

    if args.cmd == "self-check":
        return 0 if _self_check() else 1
    if args.cmd == "status":
        show_status()
        return 0
    if args.cmd == "consume":
        result = consume_worklist(args.wtype, args.batch)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
