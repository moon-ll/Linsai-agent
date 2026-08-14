#!/usr/bin/env python3
"""多端同步层 —— 把 hermes 各端（本地/飞书/Web）的产出汇聚到林赛知识库。

用途：
    定时扫描 hermes linsai profile 的新会话和文献产出，导入林赛知识库，
    使无论用户在哪个端（本地 hermes、飞书机器人、Web 界面）产生的讨论和文献，
    最终都能在林赛 CoPilot Web 端看到、检索到。

同步方向：
    hermes 产出 → 林赛知识库（单向导入，标记来源）
    - 文献产出（daily_candidates / deep_analysis）→ knowledge/raw + wiki/projects/文献简报
    - hermes 会话（sessions/）→ wiki/projects/文献简报/讨论记录（提取讨论内容）

去重机制：
    用 memory/sync-state.json 记录已同步的 session_id 和文献 arxiv_id，
    避免重复导入。

用法示例：
    >>> from sync_engine import sync_all, sync_hermes_sessions, sync_hermes_outputs
    >>> result = sync_all()                      # 全量同步
    >>> print(f"新增 {result['new_sessions']} 会话, {result['new_papers']} 文献")

程序化调用（可由 Web/API 或 cron 触发）：
    >>> from sync_engine import sync_all
    >>> sync_all()

规范：
    - 仅使用 Python 3 标准库
    - PROJECT_ROOT 通过 Path(__file__).parent.parent 推导
    - 同步是幂等的（重复运行不会重复导入）
    - 导入失败不阻塞（记录错误，继续处理其他）
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from common import now_utc as _now_utc, file_lock as _file_lock

from paths import PROJECT_ROOT, MEMORY_DIR
SYNC_STATE_PATH = MEMORY_DIR / "sync-state.json"

# hermes linsai profile 路径
HERMES_HOME = Path.home() / ".hermes"
LINSAI_PROFILE = HERMES_HOME / "profiles" / "linsai"
LINSAI_SESSIONS = LINSAI_PROFILE / "sessions"

# hermes 文献产出
HERMES_WORKSPACE = Path.home() / "Desktop" / "hermes_workspace"
BRIEFINGS_DIR = HERMES_WORKSPACE / "knowledge_base" / "AI_wiki" / "briefings"

# v6.8.14: PDF 原文 + 深度分析来源路径
HERMES_PDF_DIR = HERMES_WORKSPACE / "knowledge_base" / "AI_wiki" / "03-raw" / "papers" / "pdfs"
PDF_TARGET_DIR = PROJECT_ROOT / "knowledge" / "raw" / "pdfs"
PDF_TEXT_CACHE_DIR = PDF_TARGET_DIR / "_text_cache"
BRIEFING_REVIEWS_DIR = PROJECT_ROOT / "knowledge" / "wiki" / "reviews"


def _load_sync_state() -> Dict[str, Any]:
    """加载同步状态（记录已同步的 ID）。"""
    if not SYNC_STATE_PATH.exists():
        return {
            "synced_sessions": [],
            "synced_papers": [],
            "last_sync": "",
            "history": [],
        }
    try:
        return json.loads(SYNC_STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"synced_sessions": [], "synced_papers": [], "last_sync": "", "history": []}


def _save_sync_state(state: Dict[str, Any]) -> None:
    """保存同步状态（v6.8.0+：加跨进程锁，避免 syncEngine 多实例并发写入）。"""
    state["last_sync"] = _now_utc()
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    # v6.8.0+: 跨进程锁，防止同步引擎并发写导致丢失历史
    with _file_lock("sync-state"):
        SYNC_STATE_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
        )


def _import_kb_helper():
    """动态导入 knowledge_base 模块（供 sync_all 自动重建用）。"""
    import importlib.util
    kb_path = PROJECT_ROOT / "scripts" / "knowledge_base.py"
    spec = importlib.util.spec_from_file_location("knowledge_base", kb_path)
    kb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kb)
    return kb


def sync_hermes_sessions(max_count: int = 50) -> Dict[str, Any]:
    """同步 hermes linsai 的新会话到林赛讨论记录。

    扫描 hermes sessions/ 目录，将未同步的会话导入为讨论记录。
    跳过无实质内容的会话（如纯工具调用、空会话）。

    Args:
        max_count: 单次最多同步的会话数（防止一次导入过多）

    Returns:
        {new_sessions, skipped, errors}
    """
    # 延迟导入（避免循环依赖）
    import sys
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from kb_importer import import_session_discussion

    state = _load_sync_state()
    synced_ids = set(state.get("synced_sessions", []))

    if not LINSAI_SESSIONS.exists():
        return {"new_sessions": 0, "skipped": 0, "errors": 0, "reason": "sessions 目录不存在"}

    # 扫描会话文件（按修改时间倒序）
    session_files = sorted(
        LINSAI_SESSIONS.glob("*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    new_count = 0
    skipped = 0
    errors = 0

    for sf in session_files:
        if new_count >= max_count:
            break

        # 用文件名作为唯一标识（含时间戳，天然唯一）
        session_key = sf.stem
        if session_key in synced_ids:
            skipped += 1
            continue

        # 只同步有实质内容的会话（消息数 > 2，且含用户输入）
        try:
            data = json.loads(sf.read_text(encoding="utf-8"))
            messages = data.get("messages", [])
            has_user = any(m.get("role") == "user" for m in messages)
            if len(messages) < 3 or not has_user:
                skipped += 1
                synced_ids.add(session_key)  # 标记已处理，避免重复扫描
                continue

            # 检测平台来源
            platform = data.get("platform", "local")

            # 导入为讨论记录
            result = import_session_discussion(sf, project="文献简报")
            if result:
                new_count += 1
                synced_ids.add(session_key)
            else:
                errors += 1
                synced_ids.add(session_key)  # 失败也标记，避免反复尝试
        except Exception:
            errors += 1
            synced_ids.add(session_key)

    # 更新状态
    state["synced_sessions"] = list(synced_ids)[-500:]  # 保留最近 500 条记录
    _save_sync_state(state)

    return {"new_sessions": new_count, "skipped": skipped, "errors": errors}


def sync_hermes_outputs() -> Dict[str, Any]:
    """同步 hermes 文献产出到林赛知识库。

    扫描 daily_candidates.json，将未导入的候选论文导入 raw/papers/。
    注意：不自动导入深度解析（需用户在 Web 端勾选）。

    Returns:
        {new_papers, skipped, errors}
    """
    import sys
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from kb_importer import _load_candidates, import_candidate

    state = _load_sync_state()
    synced_papers = set(state.get("synced_papers", []))

    candidates = _load_candidates()
    papers = candidates.get("papers", [])

    if not papers:
        return {"new_papers": 0, "skipped": 0, "errors": 0, "reason": "无候选论文"}

    new_count = 0
    skipped = 0
    errors = 0

    for p in papers:
        aid = p.get("arxiv_id", "")
        if not aid:
            continue
        if aid in synced_papers:
            skipped += 1
            continue

        result = import_candidate(aid)
        if result:
            new_count += 1
            synced_papers.add(aid)
        else:
            errors += 1
            synced_papers.add(aid)

    state["synced_papers"] = list(synced_papers)[-500:]
    _save_sync_state(state)

    return {"new_papers": new_count, "skipped": skipped, "errors": errors}


# ---------------------------------------------------------------------------
# v6.8.14 WP1: PDF 原文同步
# ---------------------------------------------------------------------------

def sync_pdf_library() -> Dict[str, Any]:
    """从 hermes workspace 同步 PDF 原文到知识库。

    链 ①：hermes pdfs/*.pdf → knowledge/raw/pdfs/*.pdf + _text_cache/*.txt + _pdf-library.md

    Returns:
        {"synced": int, "skipped": int, "index_updated": bool}
    """
    import shutil

    if not HERMES_PDF_DIR.exists():
        return {"synced": 0, "skipped": 0, "index_updated": False, "reason": "hermes PDF 目录不存在"}

    PDF_TARGET_DIR.mkdir(parents=True, exist_ok=True)
    PDF_TEXT_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    synced = 0
    skipped = 0
    pdf_entries = []  # 用于索引页

    for pdf_file in sorted(HERMES_PDF_DIR.glob("*.pdf")):
        target = PDF_TARGET_DIR / pdf_file.name
        if target.exists():
            skipped += 1
        else:
            try:
                shutil.copy2(pdf_file, target)
                synced += 1
            except Exception:
                skipped += 1
                continue

        # 文本缓存（幂等——已有缓存则跳过提取）
        arxiv_raw = pdf_file.stem  # 如 2403_15337
        cache_file = PDF_TEXT_CACHE_DIR / f"{arxiv_raw}.txt"
        if not cache_file.exists():
            try:
                text = _extract_pdf_text(target)
                cache_file.write_text(text, encoding="utf-8")
            except Exception:
                pass

        pdf_entries.append({"arxiv_id": arxiv_raw.replace("_", "."), "filename": pdf_file.name})

    # 生成/更新 Obsidian 索引页
    index_updated = _update_pdf_library_index(pdf_entries)

    return {"synced": synced, "skipped": skipped, "index_updated": index_updated}


def _extract_pdf_text(pdf_path: Path) -> str:
    """从 PDF 提取文本（优先 PyMuPDF，回退 subprocess pdftotext）。"""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(pdf_path))
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return text[:50000]
    except ImportError:
        pass
    try:
        import subprocess
        result = subprocess.run(
            ["pdftotext", "-q", str(pdf_path), "-"],
            capture_output=True, text=True, timeout=30
        )
        return result.stdout[:50000]
    except Exception:
        return "(文本提取失败)"


def _update_pdf_library_index(entries: List[Dict[str, Any]]) -> bool:
    """更新 Obsidian PDF 索引页 _pdf-library.md。"""
    if not entries:
        return False

    # 尝试从 wiki/papers 获取标题
    wiki_papers_dir = PROJECT_ROOT / "knowledge" / "wiki" / "papers"
    raw_papers_dir = PROJECT_ROOT / "knowledge" / "raw" / "papers"

    lines = [
        "# PDF 全文库",
        "",
        "> 本页自动生成，汇总所有已同步的 PDF 原文。",
        f"> 最后更新：{_now_utc()}",
        "",
        f"共 **{len(entries)}** 个 PDF。",
        "",
        "| arXiv ID | 标题 | 有全文 | 有深度笔记 |",
        "|----------|------|--------|------------|",
    ]

    for e in sorted(entries, key=lambda x: x["arxiv_id"]):
        aid = e["arxiv_id"]
        # 查标题
        title = aid
        for src_dir in [raw_papers_dir, wiki_papers_dir]:
            md_file = src_dir / f"{aid}.md"
            if md_file.exists():
                try:
                    text = md_file.read_text(encoding="utf-8")[:500]
                    for line in text.split("\n"):
                        if line.startswith("title:"):
                            title = line.split(":", 1)[1].strip().strip('"\'')[:60]
                            break
                    if title != aid:
                        break
                except Exception:
                    pass

        has_note = "✓" if (wiki_papers_dir / f"{aid}.md").exists() else "—"
        lines.append(f"| `{aid}` | {title} | ✓ | {has_note} |")

    lines.append("")
    index_path = PDF_TARGET_DIR / "_pdf-library.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# v6.8.14 WP2: 每日文献简报同步
# ---------------------------------------------------------------------------

def sync_research_briefings() -> Dict[str, Any]:
    """从 hermes workspace 同步每日精选简报到知识库。

    链 ②：hermes research_briefing_*.md → knowledge/wiki/reviews/briefing-YYYY-MM-DD.md + briefing-index.md

    v6.8.51：hermes 侧 2026-06-08 后简报改名 daily_memory_YYYYMMDD.md（每日产出），
    旧命名规则再未匹配导致简报断流两个月。现同时兼容两种命名；
    同日双源时 research_briefing 优先（更完整的研究简报）。

    Returns:
        {"synced": int, "skipped": int}
    """
    import re

    if not BRIEFINGS_DIR.exists():
        return {"synced": 0, "skipped": 0, "reason": "hermes briefings 目录不存在"}

    BRIEFING_REVIEWS_DIR.mkdir(parents=True, exist_ok=True)

    synced = 0
    skipped = 0
    briefing_entries = []
    seen_dates = set()

    # v6.8.51: 双命名兼容（旧研究简报 + 新每日简报），旧命名优先
    briefing_sources = [
        ("research_briefing_*.md", "林赛研究简报"),
        ("daily_memory_*.md", "林赛每日简报"),
    ]

    for pattern, display_name in briefing_sources:
        for f in sorted(BRIEFINGS_DIR.glob(pattern)):
            # 从文件名提取日期（兼容两种格式）
            # research_briefing_2026-06-08.md → 2026-06-08
            # research_briefing_20260509.md / daily_memory_20260509.md → 2026-05-09
            name = f.stem

            date_match = re.search(r"(\d{4})[-_]?(\d{2})[-_]?(\d{2})", name)
            if date_match:
                y, m, d = date_match.groups()
                date_str = f"{y}-{m}-{d}"
            else:
                skipped += 1
                continue

            # 同日双源去重：第一个源（research_briefing）已入库则跳过
            if date_str in seen_dates:
                skipped += 1
                continue

            target = BRIEFING_REVIEWS_DIR / f"briefing-{date_str}.md"
            if target.exists():
                skipped += 1
                seen_dates.add(date_str)
                briefing_entries.append({"date": date_str, "path": target.name})
                continue

            try:
                text = f.read_text(encoding="utf-8")
                # 去重：移除已有的 frontmatter，由门面统一构建
                if text.startswith("---"):
                    end = text.find("---", 3)
                    if end > 0:
                        text = text[end + 3:].strip()

                # v6.8.51: 改走 kb_wiki 门面（此前直接 write_text 绕过门面，
                # 简报不进图谱/不写生长日志）。经 knowledge_base facade 入口
                # 以确保门面依赖（_ensure_dirs/log_growth）完成注入。
                import knowledge_base as _kb_facade
                _kb_facade.save_wiki_page(
                    f"wiki/reviews/briefing-{date_str}.md",
                    text,
                    meta={
                        "title": f"{display_name} {date_str}",
                        "type": "review",
                        "date": date_str,
                        "source": "hermes-briefing",
                    },
                )
                synced += 1
                seen_dates.add(date_str)
                briefing_entries.append({"date": date_str, "path": f"briefing-{date_str}.md"})
            except Exception:
                skipped += 1

    # 更新索引页
    if briefing_entries:
        _update_briefing_index(briefing_entries)

    return {"synced": synced, "skipped": skipped}


def _update_briefing_index(entries: List[Dict[str, Any]]) -> None:
    """更新 briefing-index.md 索引页。"""
    # 合并已有条目
    existing = []
    index_path = BRIEFING_REVIEWS_DIR / "briefing-index.md"
    if index_path.exists():
        try:
            for line in index_path.read_text(encoding="utf-8").split("\n"):
                if line.startswith("| ") and "[" in line:
                    existing.append(line)
        except Exception:
            pass

    # 去重合并
    seen_dates = set()
    all_entries = []

    # 先处理已有条目
    for line in existing:
        date_match = __import__("re").search(r"(\d{4}-\d{2}-\d{2})", line)
        if date_match:
            d = date_match.group(1)
            if d not in seen_dates:
                seen_dates.add(d)
                all_entries.append(("existing", d, line))

    # 再处理新条目
    for e in sorted(entries, key=lambda x: x["date"], reverse=True):
        d = e["date"]
        if d not in seen_dates:
            seen_dates.add(d)
            all_entries.append(("new", d, None))

    lines = [
        "# 文献简报索引",
        "",
        f"> 最后更新：{_now_utc()}",
        "",
        f"共 **{len(all_entries)}** 篇简报。",
        "",
        "| 日期 | 简报 |",
        "|------|------|",
    ]

    for kind, d, old_line in sorted(all_entries, key=lambda x: x[1], reverse=True):
        if kind == "existing" and old_line:
            lines.append(old_line)
        else:
            lines.append(f"| {d} | [[briefing-{d}]] |")

    lines.append("")
    index_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# v6.8.17: 研究趋势雷达
# ---------------------------------------------------------------------------

def _detect_research_trends() -> Dict[str, Any]:
    """v6.8.17: 研究趋势雷达——分析最近 2 周简报的关键词频率趋势。

    比较最近 7 天 vs 前 7 天的关键词出现频率，标记突增关键词。
    """
    from datetime import datetime, timezone, timedelta
    from collections import Counter

    reviews_dir = PROJECT_ROOT / "knowledge" / "wiki" / "reviews"
    if not reviews_dir.exists():
        return {"rising": [], "stable": []}

    now = datetime.now(timezone.utc)
    recent_cutoff = now - timedelta(days=7)
    older_cutoff = now - timedelta(days=14)

    # 领域关键词候选列表
    domain_keywords = [
        "HHG", "high harmonics", "strong field", "attosecond", "ultrafast",
        "moiré", "flat band", "nonlinear", "Berry phase", "topological",
        "valleytronics", "twisted", "2D material", "graphene", "TMD",
        "phase matching", "cutoff", "three-step model", "solid-state",
        "BSV", "order parameter", "quantum", "optical", "inversion",
        "symmetry", "tunneling", "recollision", "coherent",
    ]

    recent_counts = Counter()
    older_counts = Counter()

    for f in sorted(reviews_dir.glob("briefing-*.md")):
        try:
            mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
            text = f.read_text(encoding="utf-8").lower()
            for kw in domain_keywords:
                count = text.count(kw.lower())
                if count > 0:
                    if mtime > recent_cutoff:
                        recent_counts[kw] += count
                    elif mtime > older_cutoff:
                        older_counts[kw] += count
        except Exception:
            continue

    rising = []
    stable = []
    for kw in domain_keywords:
        r = recent_counts.get(kw, 0)
        o = older_counts.get(kw, 0)
        if r >= 3 and r > o * 1.5:
            rising.append({"keyword": kw, "freq": r, "recent": o})
        elif r >= 2:
            stable.append({"keyword": kw, "freq": r})

    rising.sort(key=lambda x: -x["freq"])
    return {"rising": rising[:10], "stable": stable[:10]}


def sync_all() -> Dict[str, Any]:
    """全量同步：待同步重试 + 会话 + 文献产出 + 简报状态。

    Returns:
        {new_sessions, new_papers, skipped_sessions, skipped_papers, errors, timestamp}
    """
    print("◐ 开始多端同步...")

    # [0/5] 重试失败的反向同步（CoPilot→hermes）
    print("  [0/5] 重试待同步队列...")
    try:
        import briefing_sync as bsync
        flush_result = bsync.flush_pending_reverse()
        if flush_result.get("flushed", 0) > 0:
            print(f"    重试成功 {flush_result['flushed']} 条，剩余 {flush_result['remaining']} 条")
        elif flush_result.get("remaining", 0) > 0:
            print(f"    仍有 {flush_result['remaining']} 条待重试")
        else:
            print(f"    无待同步项")
    except Exception as e:
        print(f"  ⚠ 待同步重试失败: {e}")

    print("  [1/5] 同步 hermes 会话...")
    sess_result = sync_hermes_sessions()
    print(f"    新增 {sess_result['new_sessions']} 会话, 跳过 {sess_result['skipped']}")

    print("  [2/5] 同步文献产出...")
    paper_result = sync_hermes_outputs()
    print(f"    新增 {paper_result['new_papers']} 文献, 跳过 {paper_result['skipped']}")

    # [2.6/5] PDF 原文同步（v6.8.14 WP1）
    print("  [2.6/5] 同步 PDF 原文库...")
    pdf_result = {"synced": 0, "skipped": 0}
    try:
        pdf_result = sync_pdf_library()
        print(f"    PDF 新增 {pdf_result['synced']}, 跳过 {pdf_result['skipped']}")
    except Exception as e:
        print(f"  ⚠ PDF 同步失败: {e}")

    # [3/5] 每日文献简报同步（v6.8.14 WP2）
    print("  [3/5] 同步每日文献简报...")
    briefing_sync_result = {"synced": 0, "skipped": 0}
    try:
        briefing_sync_result = sync_research_briefings()
        print(f"    简报新增 {briefing_sync_result['synced']}, 跳过 {briefing_sync_result['skipped']}")
    except Exception as e:
        print(f"  ⚠ 简报同步失败: {e}")

    # [3.5/5] 深度分析 → 5 维度笔记（v6.8.14 WP2）
    print("  [3.5/5] 转换深度分析为 5 维度笔记...")
    deep_result = {"imported": 0, "skipped": 0}
    try:
        import kb_importer
        deep_result = kb_importer.import_deep_analysis_all()
        print(f"    深度笔记新增 {deep_result['imported']}, 跳过 {deep_result['skipped']}")
    except Exception as e:
        print(f"  ⚠ 深度分析转换失败: {e}")

    # [3.6/5] 知识库笔记覆盖检测（v6.8.16 改进3）
    # v6.8.27: 持久化到看板，供前端展示
    print("  [3.6/5] 知识库笔记覆盖率检测...")
    try:
        raw_dir = PROJECT_ROOT / "knowledge" / "raw" / "papers"
        wiki_dir = PROJECT_ROOT / "knowledge" / "wiki" / "papers"
        raw_ids = {f.stem for f in raw_dir.glob("*.md")}
        wiki_ids = {f.stem for f in wiki_dir.glob("*.md")}
        missing = raw_ids - wiki_ids
        coverage = len(raw_ids & wiki_ids) / max(len(raw_ids), 1) * 100
        print(f"    笔记覆盖: {len(raw_ids & wiki_ids)}/{len(raw_ids)} ({coverage:.0f}%)")
        if missing:
            print(f"    缺失笔记: {len(missing)} 篇（将在周末输出端批量处理）")
        # v6.8.27: 写入看板供前端展示
        try:
            import json
            kanban_path = PROJECT_ROOT / "memory" / "system-kanban.json"
            if kanban_path.exists():
                kanban = json.loads(kanban_path.read_text(encoding="utf-8"))
                kanban.setdefault("kb_metrics", {})
                kanban["kb_metrics"]["coverage_pct"] = round(coverage, 1)
                kanban["kb_metrics"]["total_papers"] = len(raw_ids)
                kanban["kb_metrics"]["missing_notes"] = len(missing)
                kanban["kb_metrics"]["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                kanban_path.write_text(json.dumps(kanban, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass
    except Exception as e:
        print(f"  ⚠ 笔记覆盖率检测失败: {e}")

    # [3.7/5] 研究趋势雷达（v6.8.17 改进3）
    # v6.8.27: 持久化到看板
    print("  [3.7/5] 研究趋势雷达...")
    try:
        trends = _detect_research_trends()
        if trends.get("rising"):
            for kw in trends["rising"][:3]:
                print(f"    📈 趋势上升: {kw['keyword']} ({kw['recent']}→{kw['freq']}次)")
        # v6.8.27: 写入看板
        try:
            import json
            kanban_path = PROJECT_ROOT / "memory" / "system-kanban.json"
            if kanban_path.exists():
                kanban = json.loads(kanban_path.read_text(encoding="utf-8"))
                kanban.setdefault("kb_metrics", {})
                kanban["kb_metrics"]["trends_rising"] = [
                    {"keyword": kw["keyword"], "freq": kw["freq"]}
                    for kw in trends.get("rising", [])[:5]
                ]
                kanban["kb_metrics"]["trends_updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                kanban_path.write_text(json.dumps(kanban, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass
    except Exception as e:
        print(f"  ⚠ 趋势雷达失败: {e}")

    # [4/5] 正向同步简报状态（hermes→CoPilot）
    print("  [4/5] 同步简报状态（hermes→CoPilot）...")
    briefing_result = {"synced": 0, "skipped": 0}
    try:
        briefing_result = bsync.sync_from_hermes()
        if briefing_result.get("synced", 0) > 0:
            print(f"    状态升级 {briefing_result['synced']} 篇，跳过 {briefing_result['skipped']} 篇")
        else:
            print(f"    无状态需升级（跳过 {briefing_result.get('skipped', 0)} 篇）")
    except Exception as e:
        print(f"  ⚠ 简报状态同步失败: {e}")

    # 记录同步历史
    state = _load_sync_state()
    state["history"].append({
        "timestamp": _now_utc(),
        "new_sessions": sess_result["new_sessions"],
        "new_papers": paper_result["new_papers"],
        "briefing_synced": briefing_result.get("synced", 0),
    })
    state["history"] = state["history"][-20:]  # 保留最近 20 次记录
    _save_sync_state(state)

    total_new = sess_result["new_sessions"] + paper_result["new_papers"]

    # 同步后自动重建索引和图谱（v3.1 自维护闭环）
    # v6.8.51: 改为无条件重建——旧逻辑仅在新增论文时触发，简报/知识笔记/
    # 修复脚本等其它写入渠道不触发，导致索引与文件系统漂移（实测索引漏
    # 432 个文档长达数日）。v2 全量重建 ~2s，日频执行代价可接受。
    print("  [3/5] 重建索引和图谱...")
    try:
        import sys
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from kb_maintenance import cmd_reindex, cmd_rebuild_graph
        kb = _import_kb_helper()
        cmd_reindex(kb)
        cmd_rebuild_graph(kb)
    except Exception as e:
        print(f"  ⚠ 自动重建失败: {e}")

    if total_new > 0:
        # v3.4: 认知回流 — 从新同步的 hermes 会话中提炼记忆
        print("  [4/5] 认知回流（记忆提炼）...")
        try:
            from memory_reflow import reflow_all
            reflow_result = reflow_all(max_count=20)
            if reflow_result.get("processed", 0) > 0:
                print(f"    提炼 {reflow_result['processed']} 个会话 → {reflow_result['stats']['snippets']} 条记忆片段")
            else:
                print(f"    无新会话需提炼")
        except Exception as e:
            print(f"  ⚠ 认知回流失败: {e}")

        # v5.3: 记忆单向同步 — hermes MEMORY.md/USER.md → CoPilot
        print("  [5/5] 记忆单向同步（hermes → CoPilot）...")
        try:
            from memory_bridge import sync_memory
            mem_result = sync_memory()
            if mem_result.get("synced"):
                if mem_result.get("skipped"):
                    print(f"    记忆无变化，跳过")
                else:
                    print(f"    快照已更新（memory: {mem_result['memory_md_size']}B, 关键词: {mem_result['keywords_extracted']}）")
            else:
                print(f"    ⚠ 记忆同步失败: {mem_result.get('error', '未知')}")
        except Exception as e:
            print(f"  ⚠ 记忆同步失败: {e}")

        print(f"✓ 同步完成：新增 {total_new} 项，索引/图谱/记忆已更新")
    else:
        print("✓ 同步完成：无新增（已是最新）")

    return {
        "new_sessions": sess_result["new_sessions"],
        "new_papers": paper_result["new_papers"],
        "briefing_synced": briefing_result.get("synced", 0),
        "skipped_sessions": sess_result["skipped"],
        "skipped_papers": paper_result["skipped"],
        "errors": sess_result["errors"] + paper_result["errors"],
        "timestamp": _now_utc(),
    }


def get_sync_status() -> Dict[str, Any]:
    """返回同步状态（供 Web 展示）。"""
    state = _load_sync_state()
    return {
        "last_sync": state.get("last_sync", ""),
        "synced_sessions_count": len(state.get("synced_sessions", [])),
        "synced_papers_count": len(state.get("synced_papers", [])),
        "history": state.get("history", [])[-5:],
    }


def _self_check() -> None:
    """自检：验证同步链路（不实际导入）。"""
    print("=" * 50)
    print("◐ sync_engine 自检")
    print("=" * 50)

    print("\n[1/5] 检查数据源...")
    print(f"  hermes sessions: {'✓' if LINSAI_SESSIONS.exists() else '✗'}")
    if LINSAI_SESSIONS.exists():
        count = len(list(LINSAI_SESSIONS.glob("*.json")))
        print(f"    {count} 个会话文件")
    print(f"  hermes 文献产出: {'✓' if BRIEFINGS_DIR.exists() else '✗'}")

    print("\n[2/5] 同步状态文件...")
    state = _load_sync_state()
    print(f"  已同步会话: {len(state.get('synced_sessions', []))}")
    print(f"  已同步文献: {len(state.get('synced_papers', []))}")
    print(f"  待同步队列: {len(state.get('reverse_sync_pending', []))} 条")
    print(f"  上次同步: {state.get('last_sync', '从未')}")

    print("\n[3/5] 验证去重机制...")
    # 模拟：连续调用 sync_all 应幂等（第二次无新增）
    # 不实际调用（会修改状态），只验证函数可用
    assert callable(sync_all), "sync_all 不可调用"
    assert callable(sync_hermes_sessions), "sync_hermes_sessions 不可调用"
    assert callable(sync_hermes_outputs), "sync_hermes_outputs 不可调用"
    print("  ✓ 同步函数就绪")

    print("\n[4/5] 双向同步模块...")
    try:
        import briefing_sync as bsync
        assert callable(bsync.sync_to_hermes), "sync_to_hermes 不可调用"
        assert callable(bsync.sync_from_hermes), "sync_from_hermes 不可调用"
        assert callable(bsync.flush_pending_reverse), "flush_pending_reverse 不可调用"
        print("  ✓ briefing_sync 就绪")
    except ImportError:
        print("  ⚠ briefing_sync 未安装")

    print("\n[5/5] 同步状态查询...")
    status = get_sync_status()
    print(f"  历史记录: {len(status['history'])} 条")

    print("\n✓ sync_engine 自检通过")


if __name__ == "__main__":
    _self_check()
