#!/usr/bin/env python3
"""panel_review — 评审团模式深度修改（v6.10.46）。

背景（v6.10.14 平台期转评审团的下游缺口）：0.70-0.85 主平台带课题
"逃生阀晋级→reject_lean→人工退回"循环的主体，自动优化边际收益趋零，
需要**脱离常规 writer-critic 循环**的多角色深度修改后才能定稿。

执行者架构（v7.2.97 落地 v7.2.81 裁决）：评审团 = 执行者无关的流程
契约，评审员 = 发起评审的 agent 本身（不绑内置模型）。执行器经
memory/config/panel-executor.json 可插拔：
    - "engine"（默认）：**任务包发射器**——不调任何 LLM、不改章节文件，
      产出 06_panel/panel-task-package.md 自包含任务书；任何 agent 入口
      （协作引擎/CLI agent/人工会话）按包 + quality-review skill 第五~七节
      契约执行五步流程。cron --run-all 因此幂等零撞车、零 token 消耗。
    - "hermes"（显式 opt-in）：无人值守托底执行器——hermes 三角色编排
      （429 降级 llm_gateway panel 链），产出属自动化预审性质，重要
      课题定谳仍须引擎亲审复核。
执行者完成五步流程后用 --adopt-engine PID 走标准收尾（解析 verify
核销表清账 → 锚集守卫 → optimizing 课题晋级 pending_review + 7 天
否决窗口）。

五步流程与评审标准单一真相源见 quality-review skill 第五~七节——本脚本
只做流程编排，三角色职责/findings 输出契约（六节）、writer 修改纪律/
verify 判定格式（七节）均经 skill_loader 注入。

用法示例：
    python3 scripts/panel_review.py --status                    # 查看队列
    python3 scripts/panel_review.py --run PID                   # 跑一个课题
    python3 scripts/panel_review.py --run-all                   # 跑全部
    python3 scripts/panel_review.py --finalize PID              # 人工复核后收尾
    python3 scripts/panel_review.py --claim PID                 # 手工会话声明在场（v7.2.96）
    python3 scripts/panel_review.py --release PID               # 会话结束释放声明

并发防护（v7.2.96，治理 v7.2.82 暴露的 cron 与长跑消费者撞车）：
    1) per-proposal 非阻塞 flock（panel-<pid>）——所有经 run_panel 的
       消费者零协作互斥，锁忙温和返回 skipped=lock_busy；
    2) 06_panel/claim.json 在场声明——引擎亲审等手工会话经
       --claim/--release 声明在场，脚本消费者读到新鲜异主声明即跳过
       （TTL 防会话崩溃僵尸）。

规范：仅标准库；中文 docstring；路径经 paths 推导。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from common import file_lock, now_utc, save_json  # noqa: E402
from paths import PROJECT_ROOT  # noqa: E402

try:
    from logger import get_logger
    _log = get_logger("panel_review")
except Exception:  # pragma: no cover
    _log = None

PANEL_DIRNAME = "06_panel"
"""评审团产物目录（proposal 内，与 05_review 常规评审分离）。"""

PANEL_TIMEOUT = 600
"""单个评审角色的 hermes 超时（秒）。"""

ROLES = ["researcher", "critic", "reviewer"]
"""评审团角色：科学内容 / 红线表达 / 整体一致性。"""

PANEL_CLAIM_TTL_HOURS = 6.0
"""在场声明 TTL（小时）：手工会话/长跑消费者在 06_panel/claim.json 留下
在场声明，TTL 到期自动失效（防会话崩溃后僵尸声明永久阻塞队列）。"""

# ─────────────────────────────────────────────
# v7.2.97 执行者插拔（落地 v7.2.81 裁决：评审员=发起评审的 agent 本身）
# ─────────────────────────────────────────────
EXECUTOR_CONFIG_PATH = PROJECT_ROOT / "memory" / "config" / "panel-executor.json"
"""评审团执行器配置：{"executor": "engine" | "hermes"}。
engine（默认）= 任务包发射器（不调 LLM，任何 agent 入口按包执行）；
hermes = 显式 opt-in 的无人值守托底执行器。fail-open 默认 engine。"""


def _executor_config() -> str:
    """读取执行器配置（fail-open 默认 engine；非法值回退 engine）。"""
    try:
        from common import load_json
        cfg = load_json(EXECUTOR_CONFIG_PATH, default={})
        ex = str(cfg.get("executor", "engine")).strip().lower()
        return ex if ex in ("engine", "hermes") else "engine"
    except Exception:
        return "engine"


def _emit_task_package(proposal_id: str, prop_dir: Path, panel_dir: Path,
                       status: str, issue_block: str) -> Path:
    """v7.2.97: engine 执行器——产出自包含评审任务书（任何 agent 入口可执行）。

    任务包 = 执行者无关契约的"交接物"：核查靶子 + 流程契约/输出契约/红线
    指引 + 标准收尾命令。幂等：覆盖写（同日重发无害）。
    """
    from skill_loader import skill_path
    # v7.3.58: 零 LLM 术语扫描并入任务包（历史遗留靶子之外的自动发现层——
    # chiral/phonon 交接单实证的记号四形/术语漂移多轮漏检缺口）
    scan_block = ""
    try:
        from terminology_scanner import scan_proposal
        scan = scan_proposal(prop_dir)
        if scan.get("checked"):
            s = scan.get("summary", {})
            lines = []
            for p in scan.get("cjk_variant_pairs", [])[:6]:
                lines.append(f"- CJK 候选对: {p['a']}({p['freq_a']}) ↔ {p['b']}({p['freq_b']})"
                             f" @ {','.join(p['sections_a'][:2])}")
            for g in scan.get("token_variant_groups", [])[:6]:
                forms = " / ".join(v["form"] for v in g["variants"])
                lines.append(f"- 记号组 [{g['group_key']}]: {forms}")
            if lines:
                scan_block = (
                    f"## 程序化术语扫描靶子（terminology_scanner 零 LLM 候选，非结论——"
                    f"逐条人工/亲审核定真伪，真者入 findings 处置）\n\n" + "\n".join(lines) + "\n\n"
                )
    except Exception:
        scan_block = ""  # 扫描故障不阻塞任务包发射（fail-open）
    pkg = panel_dir / "panel-task-package.md"
    qr = skill_path("quality-review")
    pkg.write_text(
        f"# 评审团任务包（引擎亲审，v7.2.97）\n\n"
        f"- **课题**：{proposal_id}\n"
        f"- **状态**：{status}\n"
        f"- **发射时间**：{now_utc()}\n"
        f"- **执行者**：任意 agent 入口（协作引擎 / CLI agent / 人工评审会话）——\n"
        f"  按本包与 quality-review skill 契约执行，**评审员 = 你本人**：\n"
        f"  亲自读文、核查、修改、复核，不调用其它 LLM、不外包内置模型。\n\n"
        f"## 核查靶子（历史遗留问题，逐条核对当前文本是否仍存在）\n\n{issue_block}\n\n"
        f"{scan_block}"
        f"## 课题文件\n"
        f"- 章节：{prop_dir}/04_proposal/sections/ 下 rationale.md / content.md / "
        f"scheme.md / full_review.md / references.md\n"
        f"- 口径表：{prop_dir}/04_proposal/params.json（如存在 = 数值单一真相源，"
        f"相关修改必须与 canonical 一致）\n"
        f"- 待清项：{prop_dir}/05_review/params-conflicts.json（如有残留，一并核查）\n"
        f"- 预审参考（非结论）：06_panel-preaudit-*/（如有）\n\n"
        f"## 五步流程（契约全文见 {qr} 第五~七节）\n"
        f"1. **定点核查**：通读 5 章节，靶子逐条判定（引用行号+原文），新发现 ≤5 条\n"
        f"2. **深度修改**：critical/high 必修，直接编辑章节文件；数值/引用类修改\n"
        f"   必须有据（口径表/检索池/联网核实），禁止凭记忆；拿不准标「待核实」。\n"
        f"   对实质不同意的 finding 可走**辩驳-仲裁子流程**（v7.3.60）：\n"
        f"   --rebuttal-scaffold 生成脚手架 → 填反驳行 → 单点仲裁 → --arbitrate 落账\n"
        f"   （契约见 skill 七节；仲裁只扫 contested 子集，不触全轮重评）\n"
        f"3. **复核**：以修改后的磁盘文本为准逐条判定\n"
        f"4. **判定**：任一 critical/high 未解决 → 需返工；否则通过\n"
        f"5. **收尾**：运行下方标准收尾命令\n\n"
        f"## 输出契约（skill 六/七节）\n"
        f"- {panel_dir}/panel-findings.md（遗留核对表 + 新发现表）\n"
        f"- {panel_dir}/panel-verify-report.md（核销表 | 条目号 | 级别 | "
        f"已解决/部分/未解决/豁免 | 文本证据 | + 末行「复核结论: 通过/需返工」）\n\n"
        f"## 红线（skill 七节，强制）\n"
        f"- 引用三源对照零容忍（lit-gap-*.md / candidates-*.bib / reading-notes.md），\n"
        f"  池中无记录的条目一律不得写入；违反按 critical 计\n"
        f"- 口径表一致；跨章重复按「单一出处+指针」收敛；超长句仅拆句，\n"
        f"  禁改技术内容/数值/公式/引用编号\n"
        f"- 只改本课题 04_proposal/sections/ 下 5 文件 + 06_panel/ 产物\n\n"
        f"## 执行完成后的标准收尾\n\n"
        f"    python3 scripts/panel_review.py --adopt-engine {proposal_id}\n\n"
        f"（解析核销表清账 → 锚集 pairwise 守卫 → optimizing 课题晋级 "
        f"pending_review + 7 天否决窗口）\n",
        encoding="utf-8")
    return pkg

# ─────────────────────────────────────────────
# v7.2.0 评审团通过自动晋级 + 7 天否决窗口
# ─────────────────────────────────────────────
PANEL_AUTO_ADOPT_WINDOW_DAYS = 7
"""评审团复核通过晋级 pending_review 后，人工否决窗口（天）。

窗口期满未被否决 → 自动 archive（等价人工审查通过的推定形式：
评审团为引擎亲审模式 v6.10.55，复核通过即深度审查完成；窗口
保护期允许用户 veto 回退）。"""

PANEL_AUTO_ADOPT_CONFIG_PATH = PROJECT_ROOT / "memory" / "config" / "panel-auto-adopt.json"


def _panel_auto_adopt_config() -> Dict[str, Any]:
    """读取自动采纳配置（fail-open；文件缺失用默认值）。

    { "enabled": true, "window_days": 7 }
    """
    try:
        from common import load_json
        cfg = load_json(PANEL_AUTO_ADOPT_CONFIG_PATH, default={})
        return {
            "enabled": cfg.get("enabled", True),
            "window_days": cfg.get("window_days", PANEL_AUTO_ADOPT_WINDOW_DAYS),
        }
    except Exception:
        return {"enabled": True, "window_days": PANEL_AUTO_ADOPT_WINDOW_DAYS}


# ─────────────────────────────────────────────
# 队列
# ─────────────────────────────────────────────

def panel_queue() -> List[Dict[str, Any]]:
    """返回需要评审团处理的课题清单。

    v7.1.8: 同时覆盖 pending_review（旧路径，已完成一轮后人工提交）和
    optimizing+panel_review_requested（v7.1.8 r3 触发路径，未进入
    pending_review 但调度已让位）。两类按 panel_flag + critical/high
    排序：pending_review 优先（已脱圈定稿级），其次 optimizing 触发
    的（评审团路径但还在循环内）。
    """
    lc_path = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"
    data = json.loads(lc_path.read_text(encoding="utf-8"))
    out = []
    for pid, p in data.get("proposals", {}).items():
        status = p.get("status")
        # 路径 1：pending_review（人工已收尾，评审团做最终复核/补修改）
        # 路径 2：optimizing + panel_review_requested（v7.1.8 r3 自动触发）
        in_pending = status == "pending_review"
        in_panel_trigger = (
            status == "optimizing"
            and p.get("panel_review_requested")
        )
        if not (in_pending or in_panel_trigger):
            continue
        issues = [
            e for e in (p.get("open_critical_issues") or [])
            if isinstance(e, dict) and e.get("round_resolved") is None and not e.get("stale")
        ]
        # v7.1.8: 路径 2 即使无历史未解决问题也要入队（r3 触发本身就是
        # 评审信号），允许评审团主动做质量提升型深度修改；路径 1 必须有
        # 未解决问题才入队（避免对已干净的课题重复跑）。
        if not issues and not in_panel_trigger:
            continue
        # v7.1.8: 区分触发原因（report 字段）
        trigger_reason = p.get("panel_review_reason", "")
        if in_panel_trigger and "r3 触发" in trigger_reason:
            trigger = "r3_auto"
        elif in_panel_trigger:
            trigger = "platform_band"
        else:
            trigger = "manual_submit"
        out.append({
            "proposal_id": pid,
            "status": status,
            "last_score": p.get("last_score"),
            "open_issues": len(issues),
            "critical": sum(1 for e in issues if (e.get("severity") or "").lower() == "critical"),
            "high": sum(1 for e in issues if (e.get("severity") or "").lower() == "high"),
            "panel_flag": bool(p.get("panel_review_requested")),
            "trigger": trigger,
            "trigger_reason": trigger_reason[:200],
            "panel_requested_at": p.get("panel_requested_at", ""),
            "rounds": p.get("optimization_rounds", 0),
        })
    # 排序：pending_review 优先（status="pending_review" 排前），其次
    # panel_flag=True 的 optimizing，再按 critical/high 倒序
    def _sort_key(x):
        status_priority = 0 if x["status"] == "pending_review" else 1
        panel_priority = 0 if x["panel_flag"] else 1
        return (status_priority, panel_priority, -x["critical"], -x["high"])
    out.sort(key=_sort_key)
    return out


def _proposal_dir(proposal_id: str) -> Optional[Path]:
    for stage in ("pending_review", "optimizing", "drafts"):
        d = PROJECT_ROOT / "research_proposals" / stage / proposal_id
        if d.exists():
            return d
    return None


def _proposal_status(proposal_id: str) -> str:
    """读课题状态（fail-open 返回空串）。"""
    try:
        data = json.loads((PROJECT_ROOT / "research_proposals" / "_lifecycle.json")
                          .read_text(encoding="utf-8"))
        return str(data.get("proposals", {}).get(proposal_id, {}).get("status", ""))
    except Exception:
        return ""


# ─────────────────────────────────────────────
# 问题清单构建（评审团的靶子）
# ─────────────────────────────────────────────

def _load_open_issues(proposal_id: str) -> List[Dict[str, Any]]:
    lc_path = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"
    data = json.loads(lc_path.read_text(encoding="utf-8"))
    p = data.get("proposals", {}).get(proposal_id, {})
    return [
        e for e in (p.get("open_critical_issues") or [])
        if isinstance(e, dict) and e.get("round_resolved") is None and not e.get("stale")
    ]


def _build_issue_block(issues: List[Dict[str, Any]]) -> str:
    lines = []
    for i, e in enumerate(issues, 1):
        sev = (e.get("severity") or "high").upper()
        desc = str(e.get("description", ""))[:400]
        lines.append(f"{i}. [{sev}] {desc}")
    return "\n".join(lines)


# ─────────────────────────────────────────────
# v7.2.79 (C1/C2): findings 结构化聚合 + verify 结构化判定
# （契约定义见 quality-review skill 六/七节；解析失败一律 fail-open
#   退回 v6 自由文本行为，不阻塞评审团流程）
# ─────────────────────────────────────────────

_FINDING_ROW_RX = re.compile(
    r"^\|\s*P(\d+)\s*\|\s*(critical|high|medium|low)\s*\|"
    r"\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|",
    re.IGNORECASE | re.MULTILINE,
)
"""skill 六节 findings 输出契约：| P<序号> | severity | 位置 | 问题 | 建议 |"""

_VERIFY_ROW_RX = re.compile(
    r"^\|\s*([LC]\d+)[^|]*\|\s*(critical|high|medium|low)\s*\|"
    r"\s*(已解决|部分|未解决)\s*\|\s*([^|]*)\s*\|",
    re.MULTILINE | re.IGNORECASE,
)
"""skill 七节 verify 核销表契约：| 条目号 | 级别 | 判定 | 证据 |

v7.2.98: 条目号列兼容执行者附加的括注（如 `L1（Ernotte "国内学界"）`），
级别列大小写不敏感（首战实证执行者会写 `CRITICAL`）——首战两种格式偏差
均导致清账落空（kept 误报），解析器对执行者输出的**语义格式**宽容、
对**结构格式**（四列表格）严格。"""

_SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def _parse_finding_rows(findings: Dict[str, str]) -> List[Dict[str, str]]:
    """解析三角色 findings 中的结构化新发现条目（skill 六节契约）。"""
    rows: List[Dict[str, str]] = []
    for role, text in (findings or {}).items():
        if not text:
            continue
        for m in _FINDING_ROW_RX.finditer(text):
            rows.append({
                "role": role,
                "severity": m.group(2).lower(),
                "location": m.group(3).strip(),
                "issue": m.group(4).strip(),
                "advice": m.group(5).strip(),
            })
    return rows


def _aggregate_table(findings: Dict[str, str]) -> str:
    """聚合条目表（跨角色去重、severity 置顶排序）；无条目返回空串。

    去重指纹 = 位置前 20 字 + 问题前 24 字（同一问题多角色重复报告
    合并为一条，来源列保留首报角色）。
    """
    rows = _parse_finding_rows(findings)
    if not rows:
        return ""
    rows.sort(key=lambda r: _SEV_ORDER.get(r["severity"], 2))
    seen = set()
    lines = [
        "【聚合条目表（跨角色去重合并，critical/high 置顶；writer 逐条处置）】",
        "| # | 严重级 | 位置 | 问题 | 修改建议 | 来源 |",
        "|---|--------|------|------|----------|------|",
    ]
    n = 0
    for r in rows:
        fp = (r["location"][:20], r["issue"][:24])
        if fp in seen:
            continue
        seen.add(fp)
        n += 1
        lines.append(
            f"| C{n} | {r['severity']} | {r['location']} | {r['issue']} "
            f"| {r['advice']} | {r['role']} |")
    return "\n".join(lines)


def _aggregate_findings(findings: Dict[str, str]) -> str:
    """writer 输入聚合（C1）：聚合表优先，附各角色原文细节。

    解析不出任何结构化条目时 fail-open 退回 v6 原文拼接行为。
    """
    table = _aggregate_table(findings)
    tail = "\n\n---\n\n".join(
        f"## {role} 核查发现（原文）\n{f[:6000]}"
        for role, f in (findings or {}).items() if f)
    if not table:
        return "\n\n---\n\n".join(
            f"## {role} 核查发现\n{f}" for role, f in (findings or {}).items() if f)
    return table + "\n\n" + tail


def _parse_verify_verdict(verify_text: str, issue_block: str) -> str:
    """verify 结构化判定（C2）：核销表解析优先，fail-open 退回总结行。

    历史问题（L<序号>）severity 从 issue_block 反解（"1. [CRITICAL] …"）；
    聚合条目（C<序号>）级别取核销表第二列。任一 critical/high 未解决
    → 需返工；解析不出核销表行 → 退回「复核结论: 通过」字符串比对
    （v6 行为，需返工为保守默认）。
    """
    text = verify_text or ""
    summary = "通过" if "复核结论: 通过" in text else "需返工"
    rows = _VERIFY_ROW_RX.findall(text)
    if not rows:
        return summary
    sev_by_id: Dict[str, str] = {}
    for i, line in enumerate((issue_block or "").splitlines(), 1):
        m = re.match(rf"{i}\.\s*\[(\w+)\]", line.strip())
        if m:
            sev_by_id[f"L{i}"] = m.group(1).lower()
    for rid, sev, status, _ev in rows:
        if status != "未解决":
            continue
        eff_sev = sev_by_id.get(rid) or sev.lower()
        if eff_sev in ("critical", "high"):
            return "需返工"
    return "通过"


# ─────────────────────────────────────────────
# hermes 调用
# ─────────────────────────────────────────────

def _run_hermes(role: str, prompt: str, timeout: int = PANEL_TIMEOUT) -> Optional[str]:
    """调 hermes profile；429/失败时降级 llm_gateway 直连（v6.10.46）。

    hermes agent loop 的 MiniMax 每周配额耗尽时（实测 429），复核类任务
    降级走 llm_gateway（kimi/glm 链），保证评审团流程不被配额卡死。
    """
    try:
        from hermes_memory import _run_hermes_agent
        r = _run_hermes_agent(role, prompt, timeout=timeout)
        if r.get("success") and (r.get("output") or "").strip():
            return r["output"]
        err = str(r.get("error", ""))
        if _log and err:
            _log.warning("[panel] hermes %s 失败: %s", role, err[:80])
    except Exception as e:
        if _log:
            _log.warning("[panel] hermes %s 调用失败: %s", role, e)
    # 降级：llm_gateway 直连（kimi 优先，避开 MiniMax 配额）
    try:
        from llm_gateway import llm_complete
        system = f"你是评审团成员（{role} 角色）。严格按用户指令输出。"
        ok, text, meta = llm_complete(system, prompt, timeout=timeout, prefer="panel")
        if ok and text.strip():
            if _log:
                _log.info("[panel] %s 降级 llm_gateway 成功 provider=%s", role, meta.get("provider"))
            return text
    except Exception as e:
        if _log:
            _log.warning("[panel] llm_gateway 降级也失败: %s", e)
    return None


# ─────────────────────────────────────────────
# 三阶段执行
# ─────────────────────────────────────────────

def _role_skill_block(role: str) -> str:
    """v7.0.4: 按角色注入 skill 标准（评审团与常规链路共用真相源）。

    v7.2.77: role_brief/findings 输出契约沉淀至 quality-review 六节、
    修改纪律沉淀至七节——脚本不再硬编码评审方法论。注入矩阵：
    researcher → 四节（评审纪律）+ 六节（职责/契约）；
    critic → 同 researcher + nsfc-writing 十节（风格红线）；
    reviewer → 一节（四维锚点）+ 一之二（v7.2.17 校准纪律，意见映射
    编号/已修复项不重复扣分同样约束评审团）+ 四节 + 六节。fail-open。
    """
    try:
        from skill_loader import inject_block
        _qr = ["四、评审纪律", "六、评审团角色与findings契约"]
        if role == "researcher":
            return inject_block("quality-review", _qr,
                                note="评审纪律与角色职责/输出契约")
        if role == "critic":
            return inject_block("quality-review", _qr,
                                note="评审纪律与角色职责/输出契约"
                                ) + inject_block(
                "nsfc-writing", ["十、critic 检查项"],
                note="风格红线扣分依据")
        if role == "reviewer":
            return inject_block(
                "quality-review",
                ["一、四维锚点评审法", "一之二、分数锚点校准纪律"] + _qr,
                note="评审标准")
    except Exception:
        pass
    return ""


def _role_review_prompt(role: str, proposal_id: str, prop_dir: Path,
                        issue_block: str,
                        params_supplement: str = "") -> str:
    sections = ["rationale", "content", "scheme", "full_review", "references"]
    sec_files = "\n".join(
        f"- {prop_dir}/04_proposal/sections/{s}.md" for s in sections)
    out_file = f"{prop_dir}/{PANEL_DIRNAME}/panel-{role}-findings.md"
    return (
        f"你是评审团成员，对申请书做**定点核查**（不是全量重评审）。\n\n"
        f"【你的角色】{role}——职责边界以下方 skill 注入块·「三角色定点"
        f"核查职责」中 {role} 条目为准：只负责该条目范围，不越界"
        f"（researcher 不评文风；critic 不重复科学性判断；reviewer 给"
        f"修改优先级）；输出格式按 skill 注入块·「findings 输出契约」。\n\n"
        f"{_role_skill_block(role)}\n"
        f"{params_supplement}\n"
        f"【课题】{proposal_id}\n"
        f"【章节文件】\n{sec_files}\n\n"
        f"【历史遗留问题清单（核查靶子，逐条核对当前文本是否仍存在）】\n{issue_block}\n\n"
        f"【任务】\n"
        f"1. 逐条核对上述问题：仍存在（引用当前文本行）→ 已解决（说明依据）。\n"
        f"2. 核查过程中发现的**同类新问题**一并列出（不超过 5 条，避免范围膨胀）。\n"
        f"3. 每条给出可执行的修改建议（含归属章节）。\n\n"
        f"【输出】写入 {out_file}，格式：\n"
        f"# 评审团定点核查（{role}）\n\n"
        f"## 遗留问题核对\n| # | 状态 | 当前文本证据 | 修改建议 |\n\n"
        f"## 新发现问题\n（无则写'无'；有条目按 skill 注入块·findings 输出契约的表格行格式）\n\n"
        f"## 汇总\n待修/已解决条数按核对结果填写"
    )


def _params_supplement_block(prop_dir: Path) -> str:
    """v7.2.78 (B1): 评审团口径注入块——canonical 口径表 + 待清项。

    与常规链路同源（lifecycle.params_registry，单一真相源）：口径表块
    注入三角色（口径一致性是 reviewer「指标口径一致」、researcher 数值
    核查、critic 表述一致的共同核查面）；params-conflicts.json 若有
    上轮残留，作为待清项一并注入。fail-open：无表返回空串。
    """
    parts: List[str] = []
    try:
        from lifecycle.params_registry import load_params, format_params_block
        data = load_params(prop_dir)
        if data:
            parts.append(format_params_block(data))
            pc_file = prop_dir / "05_review" / "params-conflicts.json"
            if pc_file.exists():
                pc = json.loads(pc_file.read_text(encoding="utf-8"))
                conflicts = pc.get("conflicts") or []
                if conflicts:
                    lines = [
                        "\n【口径待清项（上轮落盘校验发现的旧值/旧表述残留，"
                        "评审时逐条核对当前文本是否已清）】",
                    ]
                    for c in conflicts[:10]:
                        hits = ", ".join(
                            f"{h.get('section', '?')}×{h.get('count', 0)}"
                            for h in (c.get("hits") or []))
                        lines.append(
                            f"- {c.get('key', '?')}：canonical="
                            f"{c.get('canonical', '')}，残留命中 {hits or '（见 json）'}")
                    parts.append("\n".join(lines) + "\n")
    except Exception as e:
        if _log:
            _log.debug(f"[panel] 口径注入块构建失败（fail-open）: {e}")
    return "\n".join(parts)


LONG_SENTENCE_THRESHOLD = 120
"""超长句阈值——nsfc-writing 四节句长红线（中位约 56 字、超 120 字必拆），
与 executor 写后自检门（v7.2.19）同口径。"""


def _count_long_sentences(prop_dir: Path) -> int:
    """v7.2.78 (A3): 零 LLM 超长句计数（评审团写后自检门轻量版）。

    executor 自检门依赖写前 baseline 判回弹；评审团 writer 改动面覆盖
    全部章节且无统一 baseline，这里做绝对计数（按句切分、剥 markdown
    标记后 >120 字计 1）。只覆盖正文三章（rationale/content/scheme），
    与 executor 自检门同口径。
    """
    total = 0
    sec_dir = prop_dir / "04_proposal" / "sections"
    for name in ("rationale.md", "content.md", "scheme.md"):
        f = sec_dir / name
        if not f.exists():
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for sent in re.split(r"[。！？；!?;]", text):
            stripped = re.sub(r"[#*`>\-\|\s\[\]()（）\"'“”‘’]", "", sent)
            if len(stripped) > LONG_SENTENCE_THRESHOLD:
                total += 1
    return total


def _anchor_gate(proposal_id: str) -> str:
    """v7.2.78 (B4): 自动晋级前的锚集 pairwise 守卫。

    对 rationale/scheme 两模块跑 anchor_corpus.compare_proposal（与
    review_dossier 同源：交换双跑防位置偏差、双跑不一致保守取弱）；
    任一模块最严 verdict=anchor_stronger → 返回挂起原因（不自动晋级，
    留人工裁决——机器分可漂移，真实中标本子不会）；无锚集/解析失败/
    异常一律返回空串放行（fail-open，无锚集零成本）。
    """
    try:
        from anchor_corpus import compare_proposal
        held = []
        for module in ("rationale", "scheme"):
            r = compare_proposal(proposal_id, module=module)
            if not r:
                continue
            final = r.get("final") or {}
            if final.get("verdict") == "anchor_stronger":
                anchor_name = Path(str(final.get("anchor", "?"))).stem
                gaps = "; ".join(str(g) for g in (final.get("gap_points") or [])[:2])
                held.append(f"{module} 不及锚点 {anchor_name}" + (f"（{gaps}）" if gaps else ""))
        if held:
            return "；".join(held)
    except Exception as e:
        if _log:
            _log.debug(f"[{proposal_id}] 锚集守卫异常（fail-open 放行）: {e}")
    return ""


# ─────────────────────────────────────────────
# v7.2.96 并发防护：在场声明 + per-proposal 非阻塞锁
# （治理 v7.2.82 暴露的 cron lc-panel-review 与长跑消费者并发消费同一队列）
# ─────────────────────────────────────────────

def _claim_path(proposal_id: str) -> Optional[Path]:
    prop_dir = _proposal_dir(proposal_id)
    return prop_dir / PANEL_DIRNAME / "claim.json" if prop_dir else None


def _read_fresh_claim(proposal_id: str) -> Optional[Dict[str, Any]]:
    """读取未过期的在场声明；过期/损坏/缺失一律视作无声明（None）。"""
    p = _claim_path(proposal_id)
    if not p or not p.exists():
        return None
    try:
        claim = json.loads(p.read_text(encoding="utf-8"))
        t0 = datetime.strptime(claim.get("started_at", ""),
                               "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        age_h = (datetime.now(timezone.utc) - t0).total_seconds() / 3600.0
        if age_h > PANEL_CLAIM_TTL_HOURS:
            return None
        return claim
    except Exception:
        return None


def claim_panel(proposal_id: str, consumer: str = "manual-session") -> Dict[str, Any]:
    """手工会话/外部消费者声明在场（防 cron 并发消费同一课题）。

    已有新鲜异主声明时不抢占（返回 claim_busy）——避免两个手工会话
    互踩；同 consumer 重复 claim 视为续期。
    """
    p = _claim_path(proposal_id)
    if not p:
        return {"success": False, "error": f"课题目录不存在: {proposal_id}"}
    foreign = _read_fresh_claim(proposal_id)
    if foreign and foreign.get("consumer") != consumer:
        return {"success": False, "proposal_id": proposal_id,
                "skipped": "claim_busy",
                "holder": foreign.get("consumer"),
                "started_at": foreign.get("started_at")}
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"consumer": consumer[:80], "started_at": now_utc()},
                            ensure_ascii=False, indent=2), encoding="utf-8")
    return {"success": True, "proposal_id": proposal_id, "consumer": consumer}


def release_panel_claim(proposal_id: str, consumer: str = "") -> Dict[str, Any]:
    """释放在场声明；带 consumer 时校验归属（防误删他人声明）。"""
    p = _claim_path(proposal_id)
    if not p or not p.exists():
        return {"success": True, "proposal_id": proposal_id, "released": False}
    if consumer:
        try:
            cur = json.loads(p.read_text(encoding="utf-8")).get("consumer", "")
            if cur and cur != consumer:
                return {"success": False, "proposal_id": proposal_id,
                        "error": f"声明归属 {cur}，非 {consumer}，拒绝释放"}
        except Exception:
            pass
    p.unlink(missing_ok=True)
    return {"success": True, "proposal_id": proposal_id, "released": True}


def _lock_busy_result(proposal_id: str, why: str) -> Dict[str, Any]:
    return {"success": False, "proposal_id": proposal_id,
            "skipped": "lock_busy", "reason": why}


def run_panel(proposal_id: str, dry_run: bool = False,
              consumer: str = "panel-runner") -> Dict[str, Any]:
    """对一个课题执行完整评审团流程（v7.2.96 互斥外壳）。

    双层防护（详见模块 docstring）：
    1. claim.json 新鲜异主在场声明 → 温和跳过（手工会话经 --claim 声明）；
    2. per-proposal 非阻塞 flock → 锁忙返回 skipped=lock_busy
       （与周末流水线 run_next「锁忙温和退出」同惯用法）。
    锁内重查声明并写入本消费者声明，退出（含异常路径）时清理。
    """
    prop_dir = _proposal_dir(proposal_id)
    if not prop_dir:
        return {"success": False, "error": f"课题目录不存在: {proposal_id}"}
    foreign = _read_fresh_claim(proposal_id)
    if foreign and foreign.get("consumer") != consumer:
        return _lock_busy_result(
            proposal_id,
            f"在场声明被 {foreign.get('consumer')} 持有"
            f"（started {foreign.get('started_at')}）")
    try:
        with file_lock(f"panel-{proposal_id}", blocking=False):
            # 锁内重查：抢锁间隙可能有手工会话刚写入声明
            foreign = _read_fresh_claim(proposal_id)
            if foreign and foreign.get("consumer") != consumer:
                return _lock_busy_result(
                    proposal_id,
                    f"在场声明被 {foreign.get('consumer')} 持有"
                    f"（started {foreign.get('started_at')}）")
            claim_panel(proposal_id, consumer=consumer)
            try:
                return _run_panel_impl(proposal_id, dry_run=dry_run)
            finally:
                cur = _read_fresh_claim(proposal_id)
                if cur is None or cur.get("consumer") == consumer:
                    release_panel_claim(proposal_id)
    except TimeoutError:
        return _lock_busy_result(
            proposal_id, "panel 锁被其它消费者持有（cron/runner 并发防护）")


def _run_panel_impl(proposal_id: str, dry_run: bool = False) -> Dict[str, Any]:
    """对一个课题执行完整评审团流程。"""
    prop_dir = _proposal_dir(proposal_id)
    if not prop_dir:
        return {"success": False, "error": f"课题目录不存在: {proposal_id}"}
    panel_dir = prop_dir / PANEL_DIRNAME
    panel_dir.mkdir(parents=True, exist_ok=True)

    issues = _load_open_issues(proposal_id)
    issue_block = _build_issue_block(issues)
    # v7.2.80: 允许零未解决问题课题进入主动深审——v7.1.8 已声明"评审团
    # 主动做质量提升型深度修改"意图（panel_queue 路径 2 无 issues 也入队），
    # 但此处早退使 r3 触发/显式指定的干净课题白跑返回，实现未跟上声明。
    # cron 消费不受影响：queue 路径 1 仍要求 issues 非空，路径 2 依赖
    # panel_flag（评审完成后清除）；仅显式 --run 指定的干净课题会真跑。
    issue_block = issue_block if issue_block else "（无历史遗留问题，本轮以主动深审为主：按角色职责发现新问题）"
    # v7.2.78 (B1): 口径表 + 待清项注入三角色（与常规链路同源）
    params_supp = _params_supplement_block(prop_dir)
    result: Dict[str, Any] = {"proposal_id": proposal_id, "issues": len(issues),
                              "stages": {}}
    if params_supp:
        result["params_injected"] = True

    # ── v7.2.97: engine 执行器（默认）——任务包发射器 ──
    # 评审员 = 发起评审的 agent 本身（v7.2.81 裁决）：脚本不代跑、不调
    # 任何 LLM、不改章节文件，只产出自包含任务书交任意 agent 入口执行；
    # 执行者完成后经 --adopt-engine 走标准收尾。幂等：重发覆盖无害。
    if _executor_config() == "engine":
        pkg = _emit_task_package(proposal_id, prop_dir, panel_dir,
                                 _proposal_status(proposal_id), issue_block)
        result["action"] = "task_emitted"
        result["executor"] = "engine"
        result["task_package"] = str(pkg)
        result["success"] = True
        if _log:
            _log.info(f"[{proposal_id}] 评审团任务包已发射（engine 执行器）: {pkg}")
        return result
    result["executor"] = "hermes"

    # ── 阶段 A：三角色独立评审（hermes 托底执行器，显式 opt-in）──
    findings = {}
    for role in ROLES:
        out_file = panel_dir / f"panel-{role}-findings.md"
        if out_file.exists() and out_file.stat().st_size > 500:
            findings[role] = out_file.read_text(encoding="utf-8")
            result["stages"][f"review_{role}"] = "cached"
            continue
        if dry_run:
            result["stages"][f"review_{role}"] = "dry_run"
            continue
        t0 = time.time()
        out = _run_hermes(role, _role_review_prompt(
            role, proposal_id, prop_dir, issue_block,
            params_supplement=params_supp),
            timeout=PANEL_TIMEOUT)
        if out:
            out_file.write_text(out, encoding="utf-8")
            findings[role] = out
            result["stages"][f"review_{role}"] = f"ok({time.time()-t0:.0f}s)"
        else:
            result["stages"][f"review_{role}"] = "failed"
    if not dry_run and len(findings) < 2:
        result["success"] = False
        result["error"] = "独立评审完成数 <2，中止（避免单角色偏见）"
        return result

    if dry_run:
        result["success"] = True
        return result

    # ── 阶段 B：writer 一次性深度修改 ──
    # v7.2.79 (C1): findings 聚合去重——结构化条目表置顶（critical/high
    # 前置、跨角色同题合并），附各角色原文细节；解析失败退回原文拼接。
    # 替代 v6 的 20000 字符自由文本拼接（弱聚合易诱发"改一崩二"）。
    combined = _aggregate_findings(findings)
    sections = ["rationale", "content", "scheme", "full_review", "references"]
    sec_list = "\n".join(f"- {prop_dir}/04_proposal/sections/{s}.md" for s in sections)
    mod_report = panel_dir / "panel-writer-modification-report.md"
    # v7.2.77: 修改纪律沉淀至 quality-review 七节（引用三源对照零容忍
    # 红线/口径表一致/处置取值/异源纪律），脚本只注入不再硬编码。
    writer_skill = ""
    try:
        from skill_loader import inject_block as _ib
        writer_skill = _ib("quality-review", ["七、评审团修改与复核纪律"],
                           note="修改纪律（强制执行）")
    except Exception:
        pass
    writer_prompt = (
        f"你是评审团修改执行者。以下是一份申请书的多角色定点核查发现，"
        f"请做**一次性深度修改**并输出修改报告。\n\n"
        f"【课题】{proposal_id}\n【章节文件】\n{sec_list}\n\n"
        f"{writer_skill}\n"
        f"【核查发现汇总】\n{combined[:20000]}\n\n"
        f"【执行】逐条处置核查发现（先处理聚合条目表，critical/high 必修），"
        f"直接编辑对应章节文件修复；修完后把修改报告写入 {mod_report}（逐条记录"
        f"格式见上方 skill 注入块·writer 深度修改纪律）。"
    )
    t0 = time.time()
    # v6.10.46: 产物缓存——修改报告已完整（>3KB 且非错误残留）则跳过 writer
    # （429 中断后重试时避免重复消耗 15 分钟 writer 调用）
    cached_report = (mod_report.exists() and mod_report.stat().st_size > 3000
                     and "HTTP 429" not in mod_report.read_text(encoding="utf-8", errors="ignore")[:200])
    if cached_report:
        result["stages"]["writer"] = "cached"
    else:
        wout = _run_hermes("writer", writer_prompt, timeout=900)
        if wout:
            if not mod_report.exists() or mod_report.stat().st_size < 300:
                mod_report.write_text(wout, encoding="utf-8")
            result["stages"]["writer"] = f"ok({time.time()-t0:.0f}s)"
        else:
            result["stages"]["writer"] = "failed"
            result["success"] = False
            result["error"] = "writer 深度修改失败"
            return result

    # ── 阶段 B+：writer 落盘钩子链（v7.2.78 A3）──
    # 评审团 writer 直接编辑章节文件，此前完全绕过常规链路的 executor
    # 落盘钩子（七环）——深度修改恰是"改一崩二"高发操作。此处接入三环
    # （全部 fail-open 不阻塞评审团流程；缓存命中场景同样执行，三环幂等）：
    # ① draft 同步守卫（v7.2.67 同款）② 口径落盘校验（v7.2.13 同款，
    #   冲突写 05_review/params-conflicts.json 并注入阶段 C 复核靶子）
    # ③ AI 模式写后自检门轻量版（v7.2.19 同口径：超长句 >120 字触发一次
    #   仅修句补丁，红线禁改技术内容）
    post_hook = {}
    try:
        from proposal_sections import ProposalSections as _PS
        _sec_dir = prop_dir / "04_proposal" / "sections"
        _draft = prop_dir / "04_proposal" / "proposal-draft.md"
        if _sec_dir.exists():
            _newest = max(f.stat().st_mtime for f in _sec_dir.glob("*.md"))
            if (not _draft.exists()) or (_draft.stat().st_mtime < _newest):
                _PS(prop_dir / "04_proposal").assemble_draft()
                post_hook["draft_resync"] = True
                if _log:
                    _log.info(f"[{proposal_id}] 评审团钩子：draft 落后于 sections，已重组")
    except Exception as e:
        if _log:
            _log.debug(f"[{proposal_id}] 评审团钩子 draft 同步异常（fail-open）: {e}")

    params_conflict_n = 0
    try:
        from lifecycle.params_registry import load_params as _lp, run_check_and_persist
        if _lp(prop_dir) is not None:
            _pc = run_check_and_persist(prop_dir)
            params_conflict_n = len(_pc.get("conflicts") or [])
            if params_conflict_n:
                post_hook["params_conflicts"] = params_conflict_n
                if _log:
                    _log.warning(
                        f"[{proposal_id}] 评审团钩子口径校验："
                        f"{params_conflict_n} 个旧值/旧表述残留"
                        f"（详见 05_review/params-conflicts.json，注入复核靶子）")
    except Exception as e:
        if _log:
            _log.debug(f"[{proposal_id}] 评审团钩子口径校验异常（fail-open）: {e}")

    try:
        _long_n = _count_long_sentences(prop_dir)
        if _long_n > 0:
            if _log:
                _log.warning(
                    f"[{proposal_id}] 评审团写后自检门触发：超长句 {_long_n} 处"
                    f"（> {LONG_SENTENCE_THRESHOLD} 字），发起仅修句补丁")
            _fix_prompt = (
                f"评审团 writer 刚深度修改过本申请书，落盘自检发现 {_long_n} 处"
                f"超过 {LONG_SENTENCE_THRESHOLD} 字的超长句"
                f"（文件：{prop_dir}/04_proposal/sections/ 下 rationale.md / "
                f"content.md / scheme.md）。\n"
                f"仅做拆句与衔接修复：把超长句按语义拆为 ≤100 字短句，"
                f"用内容驱动衔接（禁用「进而/据此/综上」等死板关联词）。\n"
                f"红线：禁止改动任何技术内容、数值、公式、引用编号与章节结构；"
                f"禁止引入新术语。\n"
                f"修复后直接写回原文件，只输出一行完成说明。"
            )
            _patch = _run_hermes("writer", _fix_prompt, timeout=600)
            _recheck_n = _count_long_sentences(prop_dir) if _patch else _long_n
            post_hook["long_sentences"] = f"{_long_n}→{_recheck_n}"
            if _log:
                _log.info(f"[{proposal_id}] 评审团修句补丁完成：超长句 {_long_n}→{_recheck_n}")
    except Exception as e:
        if _log:
            _log.warning(f"[{proposal_id}] 评审团写后自检门异常（fail-open）: {e}")
    if post_hook:
        result["post_hooks"] = post_hook

    # ── 阶段 C：critic 收尾复核（只验清单） ──
    verify_file = panel_dir / "panel-verify-report.md"
    # v7.2.79 (C2): verify 靶子扩为全量条目（历史 L 条目 + 聚合 C 条目）
    agg_table = _aggregate_table(findings)
    # v7.2.77: 复核判定格式沉淀至七节；一之二（v7.2.17）的意见映射
    # 编号/已修复项不重复扣分纪律同步约束收尾复核。
    verify_skill = ""
    try:
        from skill_loader import inject_block as _vb
        verify_skill = _vb("quality-review",
                           ["一之二、分数锚点校准纪律", "七、评审团修改与复核纪律"],
                           note="收尾复核判定纪律（强制执行）")
    except Exception:
        pass
    verify_prompt = (
        f"你是评审团收尾复核员。对照问题清单核查修改后的申请书（只验清单，不做全量评审）。\n\n"
        f"【章节文件】\n{sec_list}\n\n"
        f"{verify_skill}\n"
        f"【原问题清单（条目号 L<序号>，见行首编号）】\n{issue_block[:12000]}\n\n"
        + (f"【新发现聚合条目（条目号 C<序号>，须一并核销）】\n"
           f"{agg_table[:6000]}\n\n" if agg_table else "")
        + f"【修改报告】\n{(mod_report.read_text(encoding='utf-8') if mod_report.exists() else '（缺失）')[:6000]}\n\n"
        + (f"【口径落盘校验靶子】落盘后零 LLM 校验发现 {params_conflict_n} 处"
           f"旧值/旧表述残留（05_review/params-conflicts.json），逐条核对当前"
           f"文本：已清→给依据；仍残留→判未解决。\n\n" if params_conflict_n else "")
        + f"【输出】写入 {verify_file}：按 skill 注入块·verify 收尾判定的核销表"
        f"格式逐条判定（| 条目号 | 级别 | 已解决/部分/未解决 | 文本证据 |，"
        f"以修改后的磁盘文本为准，已修复项不重复计为未解决）；"
        f"末行给总结行：`复核结论: 通过`（全部解决或带合理豁免）或 "
        f"`复核结论: 需返工`（任一 critical/high 未解决，判定标准见 skill 注入块）。"
    )
    vout = _run_hermes("critic", verify_prompt, timeout=PANEL_TIMEOUT)
    if vout:
        verify_file.write_text(vout, encoding="utf-8")
    elif verify_file.exists() and "HTTP 429" in verify_file.read_text(encoding="utf-8", errors="ignore"):
        result["stages"]["verify"] = "verify_failed_429"
        result["success"] = False
        result["error"] = "收尾复核因 429 失败（writer 修改已保留，重跑将直接进入复核）"
        return result
    # v7.2.79 (C2): 结构化核销判定——核销表解析（critical/high 未解决数）
    # 优先，解析失败退回总结行字符串比对（v6 行为）
    verify_text = vout
    if not verify_text and verify_file.exists():
        try:
            verify_text = verify_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            verify_text = ""
    verdict = _parse_verify_verdict(verify_text, issue_block)
    result["stages"]["verify"] = verdict
    result["success"] = True
    result["verdict"] = verdict

    # 通过 → 清除 panel 标志恢复自动循环 + 重置评审周期
    # v7.1.8: 必须调用 reset_panel_cycle（不调的话 r3 触发条件立即又满足，
    # 评审团完成后立刻又触发一次评审团，浪费 LLM）。reset_panel_cycle
    # 标记 panel_review_completed_for_round=rounds，让下一轮 r3 再次触发
    # 需要 reset（reset 由新一轮的 lifecycle 重置或新一轮 r3 时配合清）。
    # 注意：当前 clear_panel_request 内部已记录 panel_review_completed_for_round
    # 为当前 rounds，所以新一轮 r3 触发条件已天然阻断（除非用户主动重置
    # rounds 或外部调用 reset_panel_cycle 解除标志）。这里同时调用
    # reset_panel_cycle 是为"立即重新进入下一轮评审周期"准备的接口。
    if verdict == "通过":
        try:
            from proposal_lifecycle import ProposalLifecycle
            lc = ProposalLifecycle()
            clear_r = lc.clear_panel_request(proposal_id, reason="评审团复核通过")
            result["panel_cleared"] = clear_r.get("success", False)
            reset_r = lc.reset_panel_cycle(proposal_id, reason="评审团完成后自动重置评审周期")
            result["panel_cycle_reset"] = reset_r.get("success", False)

            # v7.2.0: 评审团通过 → 自动晋级 pending_review + 决策包 + 7 天否决窗口。
            # 背景：v6.10.3 起"0.85 分数晋级"结构性不可达（monitor 实测上限 0.81），
            # 评审团通过后若无晋级通道，课题会继续在 optimizing 空转到 r8 逃生阀
            # 再被退回——3 个月仅 1 个 archived 的主因。评审团通过即深度审查完成
            # （引擎亲审 v6.10.55），晋级 pending_review 并开启否决窗口，期满自动
            # 归档。守卫：dossier 预审非 reject_lean（reject_lean = 存在未解决高危，
            # 留在 optimizing 继续改）。
            try:
                prop_state_now = lc._get_proposal_state(proposal_id) or {}
                if prop_state_now.get("status") == "optimizing":
                    cfg = _panel_auto_adopt_config()
                    if cfg.get("enabled", True):
                        # 晋级前守卫 1（零 LLM）——存在未解决高危不晋级
                        if _has_unresolved_critical(prop_state_now):
                            result["auto_promote"] = "skipped_unresolved_critical"
                            result["auto_promote_reason"] = "存在未解决 high/critical 问题，留在 optimizing 继续改"
                            if _log:
                                _log.info(
                                    f"[{proposal_id}] 评审团通过但存在未解决高危，"
                                    f"不自动晋级（留在 optimizing 继续改）"
                                )
                        elif _manual_not_ready(prop_state_now):
                            # v7.3.10: 晋级前守卫 1.5——手册未过开工就绪线不晋级
                            # （用户裁决 2026-11-02：手册决定课题能否正式开工；
                            # 补 panel 通道实现缺口，与 completion/acceptance_line 同源）
                            _mnr = _manual_not_ready(prop_state_now)
                            result["auto_promote"] = "skipped_manual_not_ready"
                            result["auto_promote_reason"] = _mnr
                            if _log:
                                _log.warning(
                                    f"[{proposal_id}] 评审团通过但手册未过开工就绪线，"
                                    f"不自动晋级: {_mnr}"
                                )
                        else:
                            # 晋级前守卫 2（v7.2.78 B4）——锚集 pairwise
                            # 对比真实范本，落败（anchor_stronger）挂起转
                            # 人工：机器分可漂移，真实中标本子不会（治
                            # Goodhart，与 review_dossier 锚集对比同源）。
                            anchor_hold = _anchor_gate(proposal_id)
                            if anchor_hold:
                                result["auto_promote"] = "held_anchor_stronger"
                                result["auto_promote_reason"] = anchor_hold
                                try:
                                    (panel_dir / "panel-anchor-verdict.md").write_text(
                                        f"# 锚集守卫挂起自动晋级（v7.2.78）\n\n"
                                        f"评审团复核通过，但锚集 pairwise 对比落败，"
                                        f"不自动晋级，留人工裁决：\n\n{anchor_hold}\n",
                                        encoding="utf-8")
                                    hold_state = lc._get_proposal_state(proposal_id) or {}
                                    hold_state["panel_anchor_hold"] = anchor_hold[:200]
                                    hold_state["panel_anchor_hold_at"] = now_utc()
                                    lc._set_proposal_state(proposal_id, hold_state)
                                except Exception:
                                    pass
                                if _log:
                                    _log.warning(
                                        f"[{proposal_id}] 评审团通过但锚集对比落败，"
                                        f"挂起自动晋级转人工: {anchor_hold}")
                            else:
                                tr = lc.transition(
                                    proposal_id, "pending_review",
                                    reason="评审团复核通过自动晋级（v7.2.0 否决窗口开启）",
                                )
                                result["auto_promote"] = "pending_review" if tr.get("success") else f"failed: {tr.get('error', '')[:80]}"
                            if tr.get("success"):
                                # 晋级后生成验收决策包 + 记录窗口起点（目录已移动，
                                # find_proposal_dir 解析新位置）
                                from review_dossier import generate_review_dossier
                                gen = generate_review_dossier(proposal_id)
                                fresh = lc._get_proposal_state(proposal_id) or {}
                                fresh["panel_auto_adopt_at"] = now_utc()
                                fresh["panel_auto_adopt_window_days"] = cfg.get("window_days", PANEL_AUTO_ADOPT_WINDOW_DAYS)
                                fresh.pop("panel_adopt_vetoed", None)
                                lc._set_proposal_state(proposal_id, fresh)
                                result["dossier_generated"] = bool(gen.get("success"))
                                if _log:
                                    _log.info(
                                        f"[{proposal_id}] 评审团通过自动晋级 pending_review，"
                                        f"{cfg.get('window_days', 7)} 天否决窗口开启"
                                    )
            except Exception as e:
                result["auto_promote"] = f"error: {str(e)[:80]}"
                if _log:
                    _log.warning(f"[{proposal_id}] 自动晋级失败（不影响评审团结果）: {e}")
        except Exception as e:
            result["panel_cleared"] = False
            result["clear_error"] = str(e)[:100]
    return result


def _open_findings_enumerated(prop_state: Dict[str, Any]) -> List[Tuple[int, Dict[str, Any]]]:
    """未解决 findings 的 1-based 枚举（与 adopt_engine/任务包靶子同序）。

    v7.3.60 批次 C 抽取为公共 helper：辩驳-仲裁的条目号必须与核销/清账
    同一序，否则裁决会记错账。
    """
    out: List[Tuple[int, Dict[str, Any]]] = []
    idx = 0
    for e in (prop_state.get("open_critical_issues") or []):
        if not (isinstance(e, dict) and e.get("round_resolved") is None and not e.get("stale")):
            continue
        idx += 1
        out.append((idx, e))
    return out


def rebuttal_scaffold(proposal_id: str) -> Dict[str, Any]:
    """批次 C（v7.3.60）：生成辩驳书脚手架——writer 对 contested 子集逐条
    填结构化反驳（条目号预填，与台账枚举同序）。零 LLM、不改台账。

    用法：writer 深度修改阶段若对某 finding 不同意，不硬修也不裸退回，
    而是填 06_panel/panel-rebuttal.md 的反驳行 → 仲裁单点复核
    （--arbitrate）→ 裁决落账。替代"争议项触发全轮重评"的旧路径。
    """
    prop_dir = _proposal_dir(proposal_id)
    if not prop_dir:
        return {"success": False, "error": f"课题目录不存在: {proposal_id}"}
    lc_path = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"
    data = json.loads(lc_path.read_text(encoding="utf-8"))
    p = data.get("proposals", {}).get(proposal_id)
    if not p:
        return {"success": False, "error": "课题未注册"}
    findings = _open_findings_enumerated(p)
    rows = "\n".join(
        f"| L{i} | {str(e.get('description', '') or e.get('issue', ''))[:60]} | "
        f"（反驳主张） | （依据：口径表/检索池/正文行号） | （建议处置） |"
        for i, e in findings
    )
    if not rows:
        rows = "（当前无未解决 findings——无需辩驳）"
    out = prop_dir / PANEL_DIRNAME / "panel-rebuttal.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        f"# 评审团辩驳书（writer → 仲裁，v7.3.60 批次 C）\n\n"
        f"- 课题：{proposal_id}\n"
        f"- 生成：{now_utc()}（脚手架，条目号与台账枚举同序）\n\n"
        f"## 填写纪律（quality-review skill 七节·辩驳-仲裁）\n"
        f"- 只对**实质不同意**的条目填行：反驳主张一句话 + 依据（口径表/"
        f"检索池/正文行号，禁止凭记忆）+ 建议处置\n"
        f"- 不填行的条目 = 默认接受 finding（按原建议修复）\n"
        f"- 仲裁单点复核仅扫本表 contested 子集，不触全轮重评\n\n"
        f"| 条目号 | finding 摘要 | 反驳主张 | 依据 | 建议处置 |\n"
        f"|---|---|---|---|---|\n"
        f"{rows}\n",
        encoding="utf-8")
    return {"success": True, "path": str(out), "open_findings": len(findings)}


_RULING_ROW_RX = re.compile(
    r"^\|\s*(?:\*\*)?([LC]\d+)(?:\*\*)?[^|]*\|\s*"
    r"(uphold_finding|uphold_rebuttal|partial)\s*\|\s*([^|]*)\s*\|",
    re.MULTILINE | re.IGNORECASE,
)


def apply_arbitration(proposal_id: str) -> Dict[str, Any]:
    """批次 C（v7.3.60）：解析 panel-arbitration.md 裁决表并落账。

    裁决语义：
      - uphold_finding：维持 finding（writer 须修复）——条目保持 open，附注
      - uphold_rebuttal：反驳成立，finding 撤销——条目清账
        （resolved_by=panel-arbitration-<date>，与引擎亲审清账同口径）
      - partial：部分成立——条目保持 open，附注仲裁理由供 writer 收窄
    fail-open：文件缺失/无裁决行 → 不动台账，返回说明。
    """
    prop_dir = _proposal_dir(proposal_id)
    if not prop_dir:
        return {"success": False, "error": f"课题目录不存在: {proposal_id}"}
    arb_file = prop_dir / PANEL_DIRNAME / "panel-arbitration.md"
    if not arb_file.exists():
        return {"success": False, "error": "无 panel-arbitration.md（仲裁未发生）"}
    text = arb_file.read_text(encoding="utf-8", errors="ignore")
    rulings: Dict[int, Tuple[str, str]] = {}
    unknown: List[str] = []
    for m in _RULING_ROW_RX.finditer(text):
        rid_raw = m.group(1).upper()
        verdict = m.group(2).lower()
        reason = m.group(3).strip()[:150]
        if not rid_raw.startswith("L"):
            unknown.append(rid_raw)
            continue
        try:
            n = int(rid_raw[1:])
        except ValueError:
            unknown.append(rid_raw)
            continue
        rulings[n] = (verdict, reason)
    if not rulings:
        return {"success": False, "error": "裁决表无可解析行（| L<n> | verdict | reason |）"}
    tag = f"panel-arbitration-{now_utc()[:10].replace('-', '')}"
    lc_path = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"
    withdrawn = held = 0
    with file_lock("lifecycle"):
        data = json.loads(lc_path.read_text(encoding="utf-8"))
        p = data.get("proposals", {}).get(proposal_id)
        if not p:
            return {"success": False, "error": "课题未注册"}
        rounds = p.get("optimization_rounds", 0)
        findings = _open_findings_enumerated(p)
        by_idx = {i: e for i, e in findings}
        for n, (verdict, reason) in rulings.items():
            e = by_idx.get(n)
            if e is None:
                unknown.append(f"L{n}")
                continue
            if verdict == "uphold_rebuttal":
                e["round_resolved"] = rounds
                e["resolved_by"] = tag
                e["resolved_note"] = f"辩驳仲裁维持反驳：{reason}"[:180]
                withdrawn += 1
            else:  # uphold_finding / partial
                e["arbitration_note"] = (
                    f"{verdict}：{reason}"[:180])
                held += 1
        data["updated_at"] = now_utc()
        save_json(lc_path, data)
    return {"success": True, "rulings": len(rulings),
            "withdrawn": withdrawn, "held": held,
            "unknown_ids": unknown, "tag": tag}


def adopt_engine_result(proposal_id: str, settle_all: bool = False) -> Dict[str, Any]:
    """v7.2.97: 引擎亲审标准收尾——解析 verify 核销表清账 + 状态机流转。

    执行者（任何 agent 入口）完成五步流程并产出 06_panel/panel-verify-report.md
    后调用本命令：
    1. 解析核销表（| L<n> | 级别 | 已解决/部分/未解决/豁免 | 证据 |）：
       「已解决」条目清账（resolved_by=engine-panel-<date>）；「部分/未解决/
       豁免」保留账本（豁免不阻断晋级，随常规轮消化）；settle_all=True 时
       全部清账（靶子清单归并过账本条目时的人工兜底）。
    2. verdict=通过 且 status=optimizing → 锚集 pairwise 守卫 →
       clear/reset → transition pending_review → 决策包 → 7 天否决窗口。
    3. verdict=需返工 → 只清「已解决」条目，保留 panel 标志待返工。
    """
    from common import save_json
    prop_dir = _proposal_dir(proposal_id)
    if not prop_dir:
        return {"success": False, "error": f"课题目录不存在: {proposal_id}"}
    verify_file = prop_dir / PANEL_DIRNAME / "panel-verify-report.md"
    if not verify_file.exists():
        return {"success": False, "error": "无 verify 报告（评审未完成，不能收尾）"}
    text = verify_file.read_text(encoding="utf-8", errors="ignore")
    verdict = "通过" if "复核结论: 通过" in text else "需返工"

    # 解析核销表 → 已解决 L 编号集合（豁免/部分/未解决不清）
    resolved_ids = set()
    for m in _VERIFY_ROW_RX.finditer(text):
        rid, _sev, status_word = m.group(1), m.group(2), m.group(3)
        if rid.startswith("L") and status_word == "已解决":
            resolved_ids.add(int(rid[1:]))

    tag = f"engine-panel-{now_utc()[:10].replace('-', '')}"
    lc_path = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"
    cleared = 0
    kept = 0
    with file_lock("lifecycle"):
        data = json.loads(lc_path.read_text(encoding="utf-8"))
        p = data.get("proposals", {}).get(proposal_id)
        if not p:
            return {"success": False, "error": "课题未注册"}
        rounds = p.get("optimization_rounds", 0)
        idx = 0
        for e in (p.get("open_critical_issues") or []):
            if not (isinstance(e, dict) and e.get("round_resolved") is None and not e.get("stale")):
                continue
            idx += 1  # 与任务包/靶子清单同序（1-based）
            if settle_all or idx in resolved_ids:
                e["round_resolved"] = rounds
                e["resolved_by"] = tag
                e["resolved_note"] = "引擎亲审轮核销，逐条明细见 06_panel/panel-verify-report.md"
                cleared += 1
            else:
                kept += 1
        p["panel_review_completed_for_round"] = rounds
        if verdict == "通过":
            p["panel_review_requested"] = False
        data["updated_at"] = now_utc()
        save_json(lc_path, data)

    result: Dict[str, Any] = {"success": True, "proposal_id": proposal_id,
                              "verdict": verdict, "cleared": cleared, "kept": kept,
                              "settle_all": settle_all}
    if verdict != "通过":
        result["action"] = "kept_optimizing_pending_rework"
        if _log:
            _log.info(f"[{proposal_id}] 亲审收尾：需返工，清 {cleared} 条，标志保留")
        return result

    # 通过 → optimizing 课题走锚集守卫 + 晋级链
    status = _proposal_status(proposal_id)
    if status != "optimizing":
        result["action"] = f"no_transition_status_{status or 'unknown'}"
        return result
    # v7.3.10: 手册开工就绪门（收尾拒绝）——与 completion/acceptance_line
    # /评审团自动晋级守卫 1.5 同源，堵住引擎亲审通道绕过手册门的缺口
    _manual_state = {}
    try:
        _lc_data = json.loads((PROJECT_ROOT / "research_proposals" / "_lifecycle.json").read_text(encoding="utf-8"))
        _manual_state = _lc_data.get("proposals", {}).get(proposal_id, {})
    except Exception:
        _manual_state = {}
    _mnr = _manual_not_ready(_manual_state)
    if _mnr:
        return {"success": False, "error": f"手册未过开工就绪线，收尾拒绝（v7.3.10）: {_mnr}"}
    anchor_hold = _anchor_gate(proposal_id)
    if anchor_hold:
        result["action"] = "held_anchor_stronger"
        result["anchor_reason"] = anchor_hold
        try:
            (prop_dir / PANEL_DIRNAME / "panel-anchor-verdict.md").write_text(
                f"# 锚集守卫挂起自动晋级（v7.2.97 引擎收尾）\n\n{anchor_hold}\n",
                encoding="utf-8")
        except Exception:
            pass
        if _log:
            _log.warning(f"[{proposal_id}] 亲审通过但锚集对比落败，挂起转人工: {anchor_hold}")
        return result
    try:
        from proposal_lifecycle import ProposalLifecycle
        lc = ProposalLifecycle()
        lc.clear_panel_request(proposal_id, reason="引擎亲审通过（v7.2.97 标准收尾）")
        lc.reset_panel_cycle(proposal_id, reason="引擎亲审完成，重置评审周期")
        tr = lc.transition(proposal_id, "pending_review",
                           reason="引擎亲审通过自动晋级（v7.2.0 否决窗口开启）")
        if tr.get("success"):
            from review_dossier import generate_review_dossier
            generate_review_dossier(proposal_id)
            fresh = lc._get_proposal_state(proposal_id) or {}
            cfg = _panel_auto_adopt_config()
            fresh["panel_auto_adopt_at"] = now_utc()
            fresh["panel_auto_adopt_window_days"] = cfg.get("window_days", PANEL_AUTO_ADOPT_WINDOW_DAYS)
            fresh.pop("panel_adopt_vetoed", None)
            lc._set_proposal_state(proposal_id, fresh)
            result["action"] = "promoted_pending_review"
        else:
            result["action"] = f"transition_failed: {str(tr.get('error', ''))[:80]}"
    except Exception as e:
        result["action"] = f"error: {str(e)[:100]}"
    if _log:
        _log.info(f"[{proposal_id}] 亲审收尾完成: {result['action']}（清 {cleared}/留 {kept}）")
    return result


def _has_unresolved_critical(prop_state: Dict[str, Any]) -> bool:
    """v7.2.0: 评审团通道晋级守卫——存在未解决 high/critical 问题即拦截。

    不复用 compute_pre_review 的完整 verdict：其"通过模块数 <= 2 →
    reject_lean"依赖 score_history 完整性，评审团触发的课题若 history
    被重置过（人工退回归零）会被永久误挡。评审团通过本身即深度审查
    完成，只需硬伤（未解决高危）拦截。
    """
    for e in (prop_state.get("open_critical_issues") or []):
        if not isinstance(e, dict):
            continue
        if e.get("round_resolved") is None and not e.get("stale"):
            if str(e.get("severity", "")).lower() in ("critical", "high"):
                return True
    return False


def _manual_not_ready(prop_state: Dict[str, Any]) -> str:
    """v7.3.10: 评审团通道晋级守卫——方法手册未过开工就绪线即拦截。

    用户裁决（2026-11-02）：手册的详细程度与完整度决定课题能否正式开工。
    panel 晋级是自动晋级的第三通道（completion/acceptance_line 均已有
    手册门，v7.3.0 实现遗漏本路径——11-03 实测 6 课题经引擎亲审绕门
    晋级）。判据与 completion 同源：score_history 中 method_manual 末条
    section_passed=True 才放行；无记录视为未过线（fail-closed）。
    返回拦截原因字符串（空串=放行）。
    """
    manual = None
    for h in reversed(prop_state.get("score_history") or []):
        if h.get("focus_section") == "method_manual":
            manual = h
            break
    if manual is None:
        return "方法手册无评审记录（method_manual 未评）"
    if not manual.get("section_passed"):
        score = manual.get("score")
        level = manual.get("manual_readiness_level")
        return (
            f"方法手册未达开工就绪（分 {score if score is not None else '?'}/"
            f"L{level if level is not None else '?'}，过线要求 ≥0.85 且 L≥3）"
        )
    return ""


def check_auto_adopt_windows(lifecycle=None) -> Dict[str, Any]:
    """v7.2.0: 扫描 pending_review 课题，评审团否决窗口期满自动归档。

    条件：panel_auto_adopt_at 存在 + 未被否决（panel_adopt_vetoed）+
    elapsed >= window_days + dossier 预审非 reject_lean。
    动作：archive_proposal（verdict=panel_auto_adopt，走既有归档链
    ——目录移动 + _archive-meta + 知识库纳入）。
    幂等：已 archived 的课题不在扫描范围。挂 lc-daily-orchestrate。
    """
    if lifecycle is None:
        from proposal_lifecycle import ProposalLifecycle
        lifecycle = ProposalLifecycle()
    cfg = _panel_auto_adopt_config()
    if not cfg.get("enabled", True):
        return {"success": True, "skipped": "disabled", "archived": []}

    archived: List[str] = []
    skipped: List[Dict[str, Any]] = []
    try:
        from datetime import datetime, timezone
        for p in lifecycle.list_by_status("pending_review"):
            pid = p["proposal_id"]
            ps = lifecycle._get_proposal_state(pid) or {}
            started = ps.get("panel_auto_adopt_at", "")
            if not started:
                continue  # 常规晋级（非评审团通道），走人工审核不变
            if ps.get("panel_adopt_vetoed"):
                skipped.append({"proposal_id": pid, "reason": "vetoed"})
                continue
            try:
                start_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
            except Exception:
                skipped.append({"proposal_id": pid, "reason": "bad_timestamp"})
                continue
            window_days = ps.get("panel_auto_adopt_window_days", cfg.get("window_days", PANEL_AUTO_ADOPT_WINDOW_DAYS))
            elapsed_days = (datetime.now(timezone.utc) - start_dt).total_seconds() / 86400.0
            if elapsed_days < window_days:
                skipped.append({
                    "proposal_id": pid,
                    "reason": "in_window",
                    "remaining_days": round(window_days - elapsed_days, 1),
                })
                continue
            # 窗口期满：终检未解决高危（窗口期内可能新增问题）
            if _has_unresolved_critical(ps):
                # 撤销窗口标记，回人工通道
                ps.pop("panel_auto_adopt_at", None)
                lifecycle._set_proposal_state(pid, ps)
                skipped.append({"proposal_id": pid, "reason": "unresolved_critical_at_expiry"})
                if _log:
                    _log.warning(f"[{pid}] 否决窗口期满但存在未解决高危，转人工审核")
                continue
            r = lifecycle.archive_proposal(
                pid,
                "评审团通过 7 天否决窗口期满自动采纳（v7.2.0）",
                "panel_auto_adopt",
            )
            if r.get("success"):
                archived.append(pid)
                # 采纳审计
                try:
                    fresh = lifecycle._get_proposal_state(pid) or {}
                    if fresh.get("review_dossier"):
                        fresh["review_dossier"]["adopted_at"] = now_utc()
                        fresh["review_dossier"]["adopted_via"] = "panel_window_expiry"
                        lifecycle._set_proposal_state(pid, fresh)
                except Exception:
                    pass
                if _log:
                    _log.info(f"[{pid}] 否决窗口期满自动归档（panel_auto_adopt）")
            else:
                skipped.append({"proposal_id": pid, "reason": f"archive_failed: {str(r.get('error', ''))[:80]}"})
    except Exception as e:
        return {"success": False, "error": str(e)[:200], "archived": archived, "skipped": skipped}
    return {"success": True, "archived": archived, "skipped": skipped}


def veto_auto_adopt(proposal_id: str, reason: str = "") -> Dict[str, Any]:
    """v7.2.0: 人工否决评审团自动采纳（窗口期内调用，阻止自动归档）。

    否决后课题留在 pending_review 走常规人工审核；再次跑评审团可通过时
    会重开新窗口。
    """
    from proposal_lifecycle import ProposalLifecycle
    lc = ProposalLifecycle()
    ps = lc._get_proposal_state(proposal_id)
    if not ps:
        return {"success": False, "error": f"proposal 未注册: {proposal_id}"}
    if ps.get("status") != "pending_review":
        return {"success": False, "error": f"课题不在 pending_review（当前 {ps.get('status')}）"}
    if not ps.get("panel_auto_adopt_at"):
        return {"success": False, "error": "该课题非评审团自动晋级通道（无窗口）"}
    with file_lock(f"proposal-{proposal_id}"):
        fresh = lc._get_proposal_state(proposal_id) or {}
        fresh["panel_adopt_vetoed"] = True
        fresh["panel_adopt_vetoed_at"] = now_utc()
        fresh["panel_adopt_veto_reason"] = reason[:200]
        fresh["updated_at"] = now_utc()
        lc._set_proposal_state(proposal_id, fresh)
    if _log:
        _log.info(f"[{proposal_id}] 评审团自动采纳被人工否决: {reason[:80]}")
    return {"success": True, "proposal_id": proposal_id, "vetoed_at": now_utc()}


def _self_check() -> None:
    q = panel_queue()
    assert isinstance(q, list)
    d = _proposal_dir("nonexistent-xyz")
    assert d is None
    # v7.2.96 在场声明生命周期（在真实第一个队列课题上演练读写删，零副作用）
    if q:
        pid = q[0]["proposal_id"]
        c = claim_panel(pid, consumer="self-check")
        assert c.get("success"), f"claim 失败: {c}"
        f = _read_fresh_claim(pid)
        assert f and f.get("consumer") == "self-check"
        r = release_panel_claim(pid, consumer="self-check")
        assert r.get("released"), f"release 失败: {r}"
        assert _read_fresh_claim(pid) is None
    print("✓ panel_review 自检通过")


def main() -> None:
    parser = argparse.ArgumentParser(description="评审团模式深度修改")
    parser.add_argument("--status", action="store_true", help="查看队列")
    parser.add_argument("--run", metavar="PID", help="跑一个课题")
    parser.add_argument("--run-all", action="store_true", help="跑全部队列")
    parser.add_argument("--finalize", metavar="PID", help="人工复核后强制收尾（清标志）")
    parser.add_argument("--dry-run", action="store_true", help="预览不调 LLM")
    parser.add_argument("--reason", default="人工确认收尾", help="--finalize 理由")
    parser.add_argument("--auto-adopt-scan", action="store_true",
                        help="v7.2.0 扫描否决窗口期满课题自动归档（挂 lc-daily-orchestrate）")
    parser.add_argument("--veto", metavar="PID",
                        help="v7.2.0 人工否决评审团自动采纳（窗口期内阻止自动归档）")
    parser.add_argument("--claim", metavar="PID",
                        help="v7.2.96 手工会话声明在场（防 cron 并发消费，配合 --consumer）")
    parser.add_argument("--release", metavar="PID",
                        help="v7.2.96 会话结束释放在场声明（配合 --consumer）")
    parser.add_argument("--consumer", default=None,
                        help="消费者标识（默认 manual-session）")
    parser.add_argument("--adopt-engine", metavar="PID", dest="adopt_engine",
                        help="v7.2.97 引擎亲审标准收尾：解析 verify 核销表清账 → "
                             "锚集守卫 → optimizing 课题晋级 pending_review + 否决窗口")
    parser.add_argument("--rebuttal-scaffold", metavar="PID",
                        help="v7.3.60 批次 C：生成辩驳书脚手架（writer 填 contested 子集反驳行）")
    parser.add_argument("--arbitrate", metavar="PID",
                        help="v7.3.60 批次 C：解析 panel-arbitration.md 裁决表并落账"
                             "（uphold_rebuttal 撤销清账 / uphold_finding·partial 保持 open 附注）")
    parser.add_argument("--settle-all", action="store_true",
                        help="v7.2.97 配合 --adopt-engine：全部未解决条目一律清账"
                             "（靶子清单归并过账本条目时的人工兜底）")
    parser.add_argument("--self-check", action="store_true", help="自检")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
        return
    if args.adopt_engine:
        r = adopt_engine_result(args.adopt_engine, settle_all=args.settle_all)
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return
    # v7.3.60 批次 C：辩驳-仲裁子流程（writer 争议点结构化反驳 + 单点仲裁落账）
    if args.rebuttal_scaffold:
        r = rebuttal_scaffold(args.rebuttal_scaffold)
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return
    if args.arbitrate:
        r = apply_arbitration(args.arbitrate)
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return
    if args.auto_adopt_scan:
        r = check_auto_adopt_windows()
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return
    if args.veto:
        r = veto_auto_adopt(args.veto, reason=args.reason)
        print(json.dumps(r, ensure_ascii=False))
        return
    if args.claim:
        r = claim_panel(args.claim, consumer=args.consumer or "manual-session")
        print(json.dumps(r, ensure_ascii=False))
        return
    if args.release:
        r = release_panel_claim(args.release, consumer=args.consumer or "")
        print(json.dumps(r, ensure_ascii=False))
        return
    if args.status:
        q = panel_queue()
        print(f"评审团队列 {len(q)} 个：")
        for e in q:
            claim = _read_fresh_claim(e["proposal_id"])
            claim_tag = f" [在场: {claim['consumer']}]" if claim else ""
            print(f"  {e['proposal_id'][:48]} score={e['last_score']} "
                  f"critical={e['critical']} high={e['high']} "
                  f"panel_flag={e['panel_flag']}{claim_tag}")
        return
    if args.finalize:
        from proposal_lifecycle import ProposalLifecycle
        lc = ProposalLifecycle()
        clear_r = lc.clear_panel_request(args.finalize, reason=args.reason)
        # v7.1.8: 人工 finalize 同步重置评审周期，允许下一轮 r3 再次触发
        reset_r = lc.reset_panel_cycle(args.finalize, reason=f"finalize: {args.reason}")
        print(json.dumps({
            "clear": clear_r,
            "reset": reset_r,
        }, ensure_ascii=False))
        return
    if args.run:
        r = run_panel(args.run, dry_run=args.dry_run)
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return
    if args.run_all:
        for e in panel_queue():
            print(f"=== {e['proposal_id']} ===", flush=True)
            # v7.2.57: 逐课题容错——单课题评审中途异常不得中断队列其余
            # 课题（cron 宿主 lc-panel-review 无人值守消费，中断即复现
            # P0-1"标志积压无消费者"形态）
            try:
                r = run_panel(e["proposal_id"], dry_run=args.dry_run)
                print(json.dumps(r, ensure_ascii=False), flush=True)
            except Exception as exc:  # noqa: BLE001
                print(json.dumps({
                    "success": False,
                    "proposal_id": e["proposal_id"],
                    "error": f"评审团运行异常（跳过继续队列）: {exc}",
                }, ensure_ascii=False), flush=True)
        return
    parser.print_help()


if __name__ == "__main__":
    main()
