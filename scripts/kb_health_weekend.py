#!/usr/bin/env python3
"""周末知识库深度健康检查（v6.7.7）。

在 kb_maintenance 基础上增加：
1. derived 内容过期检查（>30 天未复核则降级）。
2. 重复概念检测（同名/近义不同文件）。
3. unverified claims 汇总报告。
4. 来源可靠性审计。

用法：
    python3 scripts/kb_health_weekend.py
    python3 scripts/kb_health_weekend.py --apply    # 执行降级/清理
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import load_json, now_utc, save_json
from paths import PROJECT_ROOT

from knowledge_output import (
    run_kb_health_check,
    RELIABILITY_DERIVED,
    RELIABILITY_UNVERIFIED,
    UNVERIFIED_CLAIMS_PATH,
    HEALTH_REPORT_PATH,
)

try:
    from logger import get_logger
    _log = get_logger("kb_health_weekend")
except Exception:
    _log = None


def _log_info(msg: str) -> None:
    if _log:
        _log.info(msg)


def _audit_derived_pages(apply: bool = False) -> List[Dict[str, Any]]:
    """扫描 derived 页面，过期则降级为 unverified。"""
    import importlib.util
    kb_path = Path(__file__).parent / "knowledge_base.py"
    spec = importlib.util.spec_from_file_location("knowledge_base", kb_path)
    kb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kb)

    downgraded = []
    for page in kb.list_wiki_pages():
        p = kb.get_wiki_page(page.get("path", ""))
        if not p:
            continue
        fm = p.get("frontmatter", {})
        if fm.get("source_reliability") != RELIABILITY_DERIVED:
            continue
        updated = fm.get("updated_at", "")
        if not updated:
            continue
        try:
            from datetime import datetime, timezone
            dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
            days_old = (datetime.now(timezone.utc) - dt).days
            if days_old > 30:
                downgraded.append({
                    "title": fm.get("title", ""),
                    "path": page.get("path", ""),
                    "days_old": days_old,
                })
                if apply:
                    fm["source_reliability"] = RELIABILITY_UNVERIFIED
                    fm["updated_at"] = now_utc()
                    kb.save_wiki_page(page.get("path", ""), p.get("body", ""), fm)
        except Exception:
            pass

    return downgraded


def _detect_duplicate_concepts() -> List[Dict[str, Any]]:
    """检测同名/近义概念。"""
    import importlib.util
    kb_path = Path(__file__).parent / "knowledge_base.py"
    spec = importlib.util.spec_from_file_location("knowledge_base", kb_path)
    kb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kb)

    titles: Dict[str, List[str]] = {}
    for page in kb.list_wiki_pages():
        # v7.2.45 防御：title 可能来自非字符串 frontmatter 值（纯数字 title
        # 曾被类型推断成 int），此处显式转字符串避免 .lower() 抛
        # AttributeError 打断整条周末反思链。
        raw_title = page.get("title", "")
        title = str(raw_title).lower().strip()
        if not title:
            continue
        titles.setdefault(title, []).append(page.get("path", ""))

    duplicates = [{"title": k, "paths": v} for k, v in titles.items() if len(v) > 1]
    return duplicates


def _summarize_unverified() -> Dict[str, Any]:
    """汇总 unverified claims。"""
    if not UNVERIFIED_CLAIMS_PATH.exists():
        return {"count": 0, "claims": []}
    data = load_json(UNVERIFIED_CLAIMS_PATH, default={"claims": []})
    claims = data.get("claims", [])[-20:]  # 最近 20 条
    return {"count": len(data.get("claims", [])), "recent": claims}


def run_weekend_kb_health(apply: bool = False) -> Dict[str, Any]:
    """周末知识库健康检查入口。

    v6.7.7: 基础检查仍复用 knowledge_output.run_kb_health_check（与 WeekendPipeline
    output 阶段的 output_kb_health_check 共用同一实现），深度检查保留为本文件的独立 wrapper。
    """
    _log_info("开始周末知识库深度健康检查")

    # 基础健康检查（与 WeekendPipeline output 阶段 health job 共用逻辑）
    base_health = run_kb_health_check()

    # 深度检查
    derived_overdue = _audit_derived_pages(apply=apply)
    duplicates = _detect_duplicate_concepts()
    unverified = _summarize_unverified()

    report = {
        "checked_at": now_utc(),
        "base_health": base_health,
        "derived_overdue": derived_overdue,
        "derived_downgraded": apply,
        "duplicate_concepts": duplicates,
        "unverified_claims": unverified,
        "recommendations": [],
    }

    if derived_overdue:
        report["recommendations"].append(
            f"有 {len(derived_overdue)} 个 derived 页面超过 30 天未复核，建议人工确认或已自动降级"
        )
    if duplicates:
        report["recommendations"].append(
            f"发现 {len(duplicates)} 组重复/近义概念，建议合并"
        )
    if unverified["count"] > 0:
        report["recommendations"].append(
            f"有 {unverified['count']} 条 unverified claims 待人工复核"
        )

    save_json(HEALTH_REPORT_PATH, report)
    _log_info(f"周末健康检查完成: derived_overdue={len(derived_overdue)}, duplicates={len(duplicates)}")
    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="周末知识库深度健康检查")
    parser.add_argument("--apply", action="store_true", help="执行降级/清理")
    args = parser.parse_args()

    result = run_weekend_kb_health(apply=args.apply)
    print(json.dumps(result, ensure_ascii=False, indent=2))
