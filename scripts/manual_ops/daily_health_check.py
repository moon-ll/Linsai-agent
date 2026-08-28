#!/usr/bin/env python3
"""daily_health_check.py — 每日全链路健康检查与汇总报告（v6.7+ 林赛总控·每日体检）。

薄壳脚本：复用现有健康检查模块（profile_health / kb_health / failure_analyzer /
proposal_lifecycle.run_health_check），加 4 段自检（环境/产物/凭据/队列），
汇成一份 markdown 报告 + 3 行推送口径。

检查维度（7 段）：
1. 环境 — Python 版本、磁盘用量、关键目录存在
2. Provider 凭据 — MINIMAX_API_KEY / GLM_API_KEY 是否在 .env 且非空
3. 提案生命周期 — 4 个状态 proposal 数、pending_review 告警、optimizing 孤儿
4. 6 阶段产物完整性 — 每个 optimizing proposal 关键产物是否存在/非空
5. Profile 健康 — 7 个 profile 状态/24h 成功率
6. 知识库 + 失败模式 — KB 综合健康度 + 24h 错误聚类
7. 生命周期 cron — 检查 lc-micro-scheduler / lc-weekend-* 是否已注册

用法:
    python3 scripts/daily_health_check.py                  # 跑全量 + 写报告
    python3 scripts/daily_health_check.py --dry-run        # 只打印，不写报告
    python3 scripts/daily_health_check.py --archive-dir X  # 自定义归档目录

无第三方依赖。仅标准库。
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

# 项目内导入
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from common import now_utc, load_json  # noqa: E402
from paths import LOGS_DIR, MEMORY_DIR, RESEARCH_PROPOSALS_DIR  # noqa: E402

# 尝试加载现有健康模块；任意一个失败不影响整体报告，只在该段标 ⚠
try:
    from profile_health import compute_profile_health
except Exception as e:  # pragma: no cover
    compute_profile_health = None
    _PROFILE_HEALTH_IMPORT_ERR = e
try:
    # kb_health 有门面注入依赖：必须先 import knowledge_base 一次，让它注入
    # get_growth_candidates / get_growth_log，再调 get_kb_health
    import knowledge_base  # noqa: F401
    from kb_health import get_kb_health
except Exception as e:  # pragma: no cover
    get_kb_health = None
    _KB_HEALTH_IMPORT_ERR = e
try:
    from failure_analyzer import analyze_failures
except Exception as e:  # pragma: no cover
    analyze_failures = None
    _FAILURE_ANALYZER_IMPORT_ERR = e
try:
    import hermes_bridge as hb
except Exception as e:  # pragma: no cover
    hb = None
    _HB_IMPORT_ERR = e
try:
    from proposal_lifecycle import ProposalLifecycle
except Exception as e:  # pragma: no cover
    ProposalLifecycle = None
    _LIFECYCLE_IMPORT_ERR = e

# ─────────────────────────────────────────────
# 状态图标（与 AGENTS.md 规范一致）
# ─────────────────────────────────────────────
OK = "✓"
WARN = "⚠"
FAIL = "✗"
PEND = "○"

# 6 阶段产物清单（每个 proposal 应有）
PIPELINE_STAGES = [
    ("00_proposal-brief.md", "项目简报"),
    ("01_direction", "方向校准"),
    ("02_literature", "文献调研"),
    ("03_question", "科学问题"),
    ("04_proposal", "申请书主体"),
    ("05_review", "质量自检"),
]


# ─────────────────────────────────────────────
# 1. 环境自检
# ─────────────────────────────────────────────
def check_environment() -> Dict[str, Any]:
    """Python 版本、磁盘、关键目录。"""
    py_ver = ".".join(str(x) for x in sys.version_info[:3])
    py_ok = sys.version_info >= (3, 8)

    disk = shutil.disk_usage(PROJECT_ROOT)
    disk_free_gb = round(disk.free / 1024 ** 3, 1)
    disk_warn = disk_free_gb < 5.0  # < 5GB 告警

    key_dirs = ["scripts", "memory", "logs", "research_proposals", "knowledge"]
    missing_dirs = [d for d in key_dirs if not (PROJECT_ROOT / d).exists()]

    return {
        "status": OK if (py_ok and not disk_warn and not missing_dirs) else WARN,
        "python": py_ver,
        "disk_free_gb": disk_free_gb,
        "missing_dirs": missing_dirs,
    }


# ─────────────────────────────────────────────
# 2. Provider 凭据自检
# ─────────────────────────────────────────────
def check_provider_credentials() -> Dict[str, Any]:
    """检查 .env 中关键 provider 凭据是否存在且非空。"""
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return {"status": FAIL, "providers": {}, "reason": ".env 不存在"}

    env_keys = ["MINIMAX_API_KEY", "GLM_API_KEY"]
    providers: Dict[str, Dict[str, Any]] = {}

    # 实际读 .env 文件（不靠 os.environ，因为 parent 进程可能未 load）
    env_lines = env_path.read_text(encoding="utf-8").splitlines()
    env_values: Dict[str, str] = {}
    for line in env_lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env_values[k.strip()] = v.strip()

    for key in env_keys:
        v = env_values.get(key, "")
        present = bool(v)
        masked = (v[:4] + "..." + v[-4:]) if len(v) > 12 else ("<empty>" if not v else "<short>")
        providers[key] = {"present": present, "masked": masked}

    all_ok = all(p["present"] for p in providers.values())
    any_ok = any(p["present"] for p in providers.values())
    status = OK if all_ok else (WARN if any_ok else FAIL)

    return {"status": status, "providers": providers}


# ─────────────────────────────────────────────
# 3. 提案生命周期 + 4 段产物完整性
# ─────────────────────────────────────────────
def check_lifecycle_and_artifacts() -> Dict[str, Any]:
    """4 个状态 proposal 数 + 每个 optimizing 的 6 阶段产物完整性。"""
    if ProposalLifecycle is None:
        return {"status": WARN, "reason": f"无法导入 ProposalLifecycle: {_LIFECYCLE_IMPORT_ERR}"}

    try:
        lc = ProposalLifecycle()
        health = lc.run_health_check()
    except Exception as e:
        return {"status": FAIL, "reason": f"run_health_check 失败: {e}"}

    # 4 段产物完整性
    optimizing_dir = RESEARCH_PROPOSALS_DIR / "optimizing"
    artifact_status: List[Dict[str, Any]] = []
    for pdir in sorted(optimizing_dir.iterdir() if optimizing_dir.exists() else []):
        if not pdir.is_dir():
            continue
        existing = {p.name for p in pdir.iterdir() if p.is_file() or p.is_dir()}
        missing = [s[0] for s in PIPELINE_STAGES if s[0] not in existing]
        artifact_status.append({
            "proposal_id": pdir.name,
            "missing_stages": missing,
            "complete": len(missing) == 0,
        })

    incomplete = [a for a in artifact_status if not a["complete"]]
    stats = health.get("stats") or {}
    by_status = stats.get("by_status") or health.get("by_status") or health.get("state_counts") or {}
    has_alerts = bool(health.get("alerts"))
    status = OK if not incomplete and not has_alerts else WARN

    return {
        "status": status,
        "state_counts": by_status,
        "alerts": health.get("alerts", []),
        "artifacts": artifact_status,
        "incomplete_count": len(incomplete),
    }


# ─────────────────────────────────────────────
# 4. Profile 健康
# ─────────────────────────────────────────────
def check_profiles() -> Dict[str, Any]:
    """7 个 profile 状态 + 24h 成功率。"""
    if compute_profile_health is None:
        return {"status": WARN, "reason": f"无法导入 profile_health: {_PROFILE_HEALTH_IMPORT_ERR}"}

    try:
        result = compute_profile_health(window_hours=24)
    except Exception as e:
        return {"status": FAIL, "reason": f"compute_profile_health 失败: {e}"}

    profiles = result.get("profiles", {})
    blocked = [k for k, v in profiles.items() if v.get("status") == "blocked"]
    offline = [k for k, v in profiles.items() if v.get("status") == "offline"]

    if offline:
        status = FAIL
    elif blocked:
        status = WARN
    else:
        status = OK

    return {
        "status": status,
        "profiles": profiles,
        "blocked": blocked,
        "offline": offline,
        "computed_at": result.get("computed_at"),
    }


# ─────────────────────────────────────────────
# 5. 知识库健康
# ─────────────────────────────────────────────
def check_kb() -> Dict[str, Any]:
    """KB 综合健康度。"""
    if get_kb_health is None:
        return {"status": WARN, "reason": f"无法导入 kb_health: {_KB_HEALTH_IMPORT_ERR}"}

    try:
        kb = get_kb_health()
    except Exception as e:
        return {"status": FAIL, "reason": f"get_kb_health 失败: {e}"}

    # 综合健康度 — kb_health 没现成总评分，用 4 个分项合成
    #   connectivity [0..2, 越高越好] → 归一化到 [0..1]
    #   覆盖率 [0..1]
    #   别名命中率 [0..1]
    #   孤儿率 [0..1, 越低越好]
    nodes = kb.get("graph_nodes", 0) or 0
    orphans = kb.get("graph_orphans", 0) or 0
    orphan_rate = (orphans / nodes) if nodes else 0.0
    connectivity_score = min(1.0, (kb.get("graph_connectivity", 0) or 0) / 1.5)
    coverage = (kb.get("category_coverage") or {}).get("coverage_rate", 0.0) or 0.0
    hit_rate = (kb.get("alias_hit_rate") or {}).get("hit_rate", 0.0) or 0.0
    composite = round(
        0.30 * connectivity_score
        + 0.30 * coverage
        + 0.20 * hit_rate
        + 0.20 * (1.0 - orphan_rate),
        3,
    )
    if composite >= 0.7:
        status = OK
    elif composite >= 0.4:
        status = WARN
    else:
        status = FAIL

    return {
        "status": status,
        "composite_health": composite,
        "components": {
            "connectivity": connectivity_score,
            "category_coverage": coverage,
            "alias_hit_rate": hit_rate,
            "orphan_rate": orphan_rate,
        },
        "summary": {
            "raw_count": kb.get("raw_count"),
            "wiki_count": kb.get("wiki_count"),
            "graph_nodes": kb.get("graph_nodes"),
            "graph_edges": kb.get("graph_edges"),
            "graph_orphans": kb.get("graph_orphans"),
            "week_new": kb.get("week_new"),
            "pending_distill": kb.get("pending_distill"),
        },
    }


# ─────────────────────────────────────────────
# 6. 失败模式（24h）
# ─────────────────────────────────────────────
def check_failures() -> Dict[str, Any]:
    """24h 错误聚类。"""
    if analyze_failures is None:
        return {"status": WARN, "reason": f"无法导入 failure_analyzer: {_FAILURE_ANALYZER_IMPORT_ERR}"}

    try:
        result = analyze_failures(window_hours=24)
    except Exception as e:
        return {"status": FAIL, "reason": f"analyze_failures 失败: {e}"}

    summary = result.get("summary", {})
    total_errors = summary.get("total_errors", 0)
    status = OK if total_errors == 0 else (WARN if total_errors < 5 else FAIL)

    # 只保留有 occurrences 的模式
    patterns = [p for p in result.get("patterns", []) if p.get("occurrences", 0) > 0]

    return {
        "status": status,
        "total_errors": total_errors,
        "total_warnings": summary.get("total_warnings", 0),
        "top_pattern": summary.get("top_pattern"),
        "patterns": patterns,
    }


# ─────────────────────────────────────────────
# 7. 生命周期 cron 状态
# ─────────────────────────────────────────────
def check_cron() -> Dict[str, Any]:
    """检查生命周期 cron 是否已注册。"""
    if hb is None:
        return {"status": WARN, "reason": f"无法导入 hermes_bridge: {_HB_IMPORT_ERR}"}

    try:
        crons = hb.cron_list_profile("linsai")
    except Exception as e:
        return {"status": WARN, "reason": f"cron_list_profile 失败: {e}"}

    # 期望的生命周期 cron 名称前缀
    required_prefixes = ["lc-micro-scheduler", "lc-weekend-"]
    found: List[str] = []
    missing: List[str] = []

    for prefix in required_prefixes:
        matched = [c.get("name", "") for c in crons if c.get("name", "").startswith(prefix)]
        if matched:
            found.extend(matched)
        else:
            missing.append(prefix)

    # 至少需要 micro-scheduler 和 1 个 weekend cron 才算正常
    has_micro = any("lc-micro-scheduler" in n for n in found)
    has_weekend = any("lc-weekend" in n for n in found)

    if has_micro and has_weekend:
        status = OK
    elif not has_micro and not has_weekend:
        status = FAIL
    else:
        status = WARN

    return {
        "status": status,
        "found": found,
        "missing": missing,
        "count": len(crons),
        "setup_command": "python3 scripts/proposal_lifecycle.py --setup-cron-v2",
    }


# ─────────────────────────────────────────────
# 汇总 + 渲染 markdown
# ─────────────────────────────────────────────
def render_report(sections: Dict[str, Dict[str, Any]], date_str: str) -> Tuple[str, str]:
    """渲染 markdown 报告 + 一句话总结。"""
    env = sections["environment"]
    cred = sections["credentials"]
    lc = sections["lifecycle"]
    prof = sections["profiles"]
    kb = sections["kb"]
    fail = sections["failures"]
    cron = sections.get("cron", {"status": PEND, "found": []})

    # 整体状态：任一 FAIL 则 FAIL，并列 WARN 则 WARN
    statuses = [s["status"] for s in sections.values()]
    if FAIL in statuses:
        overall = FAIL
    elif WARN in statuses:
        overall = WARN
    else:
        overall = OK

    md = [
        f"# 每日健康检查 · {date_str}",
        "",
        f"## 0. 一句话总结",
        "",
        f"**整体状态** {overall}",
        "",
        "| 段 | 状态 | 关键指标 |",
        "|---|---|---|",
        f"| 1. 环境 | {env['status']} | Python {env['python']}, 磁盘 {env['disk_free_gb']}GB free |",
        f"| 2. Provider 凭据 | {cred['status']} | {len([p for p in cred['providers'].values() if p['present']])}/{len(cred['providers'])} 配置 |",
        f"| 3. 生命周期+产物 | {lc['status']} | 4 段状态={lc.get('state_counts', {})}, 缺产物 {lc.get('incomplete_count', 0)} 个 |",
        f"| 4. Profile | {prof['status']} | blocked={len(prof.get('blocked', []))}, offline={len(prof.get('offline', []))} |",
        f"| 5. 知识库 | {kb['status']} | 综合分 {kb.get('composite_health', '?')} |",
        f"| 6. 失败模式 | {fail['status']} | 24h 错误 {fail.get('total_errors', 0)} |",
        f"| 7. 生命周期 cron | {cron['status']} | 已注册 {len(cron.get('found', []))} 个, 缺 {len(cron.get('missing', []))} 个 |",
        "",
    ]

    # 1. 环境
    md += [
        "## 1. 环境",
        "",
        f"- **Python**: `{env['python']}` {OK if env['status'] != FAIL else FAIL}",
        f"- **磁盘剩余**: {env['disk_free_gb']} GB {WARN if env['disk_free_gb'] < 5 else OK}",
        f"- **缺失目录**: {env['missing_dirs'] or '无'}",
        "",
    ]

    # 2. 凭据
    md += [
        "## 2. Provider 凭据",
        "",
        "| Key | 状态 | 脱敏值 |",
        "|---|---|---|",
    ]
    for k, v in cred["providers"].items():
        md.append(f"| `{k}` | {OK if v['present'] else FAIL} | `{v['masked']}` |")
    if "reason" in cred:
        md.append(f"\n**注意**: {cred['reason']}")
    md.append("")

    # 3. 生命周期 + 产物
    md += [
        "## 3. 提案生命周期 + 6 阶段产物",
        "",
        f"- **状态分布**: {lc.get('state_counts', {})}",
        f"- **告警**: {len(lc.get('alerts', []))} 条",
    ]
    for a in lc.get("alerts", []):
        md.append(f"  - {a}")
    md += [
        "",
        "**6 阶段产物完整性**（optimizing 区）",
        "",
        "| Proposal | 缺阶段 | 完整 |",
        "|---|---|---|",
    ]
    for art in lc.get("artifacts", []):
        complete_icon = OK if art["complete"] else WARN
        md.append(f"| `{art['proposal_id']}` | {', '.join(art['missing_stages']) or '—'} | {complete_icon} |")
    md.append("")

    # 4. Profile
    md += [
        "## 4. Profile 健康（7 个）",
        "",
        "| Profile | 状态 | 24h 成功率 | 派活数 | 最近错误 |",
        "|---|---|---|---|---|",
    ]
    for name, p in prof.get("profiles", {}).items():
        sr = p.get("success_rate_24h")
        sr_str = f"{sr * 100:.0f}%" if isinstance(sr, (int, float)) else "—"
        md.append(
            f"| `{name}` | {p.get('status', '?')} | {sr_str} | "
            f"{p.get('dispatch_count_24h', 0)} | "
            f"`{(p.get('recent_error') or '—')[:60]}` |"
        )
    md.append("")

    # 5. KB
    md += [
        "## 5. 知识库健康",
        "",
        f"- **综合分**: {kb.get('composite_health', '?')}",
        "",
    ]
    if "reason" in kb:
        md.append(f"**注意**: {kb['reason']}\n")

    # 6. 失败模式
    md += [
        "## 6. 失败模式（24h）",
        "",
        f"- **总错误数**: {fail.get('total_errors', 0)}",
        f"- **总警告数**: {fail.get('total_warnings', 0)}",
        f"- **Top pattern**: {fail.get('top_pattern') or '—'}",
        "",
    ]
    if fail.get("patterns"):
        md += [
            "| Pattern | 类别 | 出现次数 |",
            "|---|---|---|",
        ]
        for p in fail["patterns"]:
            md.append(f"| `{p['id']}` | {p.get('category', '')} | {p.get('occurrences', 0)} |")
    md.append("")

    # 7. 生命周期 cron
    md += [
        "## 7. 生命周期 cron",
        "",
        f"- **总 cron 数**: {cron.get('count', '?')}",
        f"- **已注册**: {', '.join(cron.get('found', [])) or '无'}",
        f"- **缺失前缀**: {', '.join(cron.get('missing', [])) or '无'}",
        "",
    ]
    if cron.get("missing"):
        md += [
            f"- 修复命令: `{cron['setup_command']}`",
            "",
        ]

    # 建议动作（按优先级排序）
    actions = []
    if cred["status"] != OK:
        miss = [k for k, v in cred["providers"].items() if not v["present"]]
        actions.append(f"修复 provider 凭据: {', '.join(miss)}")
    if prof.get("offline"):
        actions.append(f"恢复 offline profile: {', '.join(prof['offline'])}")
    if lc.get("incomplete_count", 0) > 0:
        actions.append(f"补全 {lc['incomplete_count']} 个 optimizing proposal 的缺失阶段产物")
    if fail.get("total_errors", 0) > 0:
        actions.append(f"查看 24h 失败模式: {fail.get('top_pattern')}")
    if prof.get("blocked"):
        actions.append(f"检查 blocked profile: {', '.join(prof['blocked'])}")
    if kb["status"] != OK:
        actions.append(f"知识库综合分 {kb.get('composite_health', '?')} 偏低，建议执行 kb_maintenance.py --weekly")
    if cron.get("missing"):
        actions.append(f"生命周期 cron 缺失前缀: {', '.join(cron['missing'])}，执行 {cron['setup_command']}")
    if not actions:
        actions.append("全绿，无需即时动作")

    md += [
        "## 建议动作",
        "",
    ]
    for i, a in enumerate(actions, 1):
        md.append(f"{i}. {a}")
    md += ["", f"_Powered by daily_health_check.py · {now_utc()}_", ""]

    body = "\n".join(md)

    # 一句话总结（<= 200 字）
    headline = (
        f"[{overall}] 全链路体检完成 — "
        f"环境{env['status']} 凭据{cred['status']} 链路{lc['status']} "
        f"profiles{prof['status']} KB{kb['status']} 失败{fail['status']} "
        f"cron{cron['status']}"
    )
    if overall != OK:
        headline += f"\n→ 首要动作: {actions[0]}"

    return body, headline


def main() -> int:
    parser = argparse.ArgumentParser(description="每日全链路健康检查")
    parser.add_argument("--dry-run", action="store_true", help="只打印，不写报告")
    parser.add_argument("--archive-dir", default="research_proposals/_archive/health",
                        help="报告归档目录（相对 PROJECT_ROOT）")
    args = parser.parse_args()

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"[daily_health_check] 启动 · {date_str}", flush=True)

    # 6 段并行能力没有，串行跑（每个 ~1-2s，总 6-12s）
    sections: Dict[str, Dict[str, Any]] = {}
    for name, fn in [
        ("environment", check_environment),
        ("credentials", check_provider_credentials),
        ("lifecycle", check_lifecycle_and_artifacts),
        ("profiles", check_profiles),
        ("kb", check_kb),
        ("failures", check_failures),
        ("cron", check_cron),
    ]:
        print(f"  [{name}] running...", flush=True)
        try:
            sections[name] = fn()
        except Exception as e:
            sections[name] = {"status": FAIL, "reason": f"未捕获异常: {e}"}
        print(f"  [{name}] {sections[name]['status']}", flush=True)

    body, headline = render_report(sections, date_str)

    print("\n" + "=" * 60)
    print(headline)
    print("=" * 60)

    if args.dry_run:
        print("\n[dry-run] 不写报告")
        return 0

    archive_dir = PROJECT_ROOT / args.archive_dir
    archive_dir.mkdir(parents=True, exist_ok=True)
    report_path = archive_dir / f"{date_str}.md"
    report_path.write_text(body, encoding="utf-8")
    print(f"\n[report] 写入: {report_path}")

    # JSON 索引（便于程序化消费）
    json_path = archive_dir / f"{date_str}.json"
    json_path.write_text(
        json.dumps(sections, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"[json]   写入: {json_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
