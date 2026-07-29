from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import subprocess
import time as _time

from common import now_utc, file_lock, hermes_subprocess_env

import proposal_lifecycle as _pl

from proposal_lifecycle.constants import (
    _log,
    DEFAULT_STAGGER_SECONDS,
    LIFECYCLE_STAGES,
    PROJECT_TYPES,
    PROPOSALS_ROOT,
)


class CronMixin:
    # ------------------------------------------------------------------
    # cron 自动驱动（多 cron 分解架构，v6.5.2）
    # ------------------------------------------------------------------

    def match_proposals_with_brief(
        self,
        brief_path: Optional[str] = None,
        brief_content: Optional[str] = None,
    ) -> List[str]:
        """文献-课题匹配（v6.6.2）：判断当天简报与哪些 optimizing 课题相关。

        匹配逻辑：提取简报关键词（子方向/related标签），与每个课题的
        proposal-brief（标题+核心问题+创新点）做关键词重叠匹配。

        Args:
            brief_path: 简报文件路径；为None时自动找最新简报
            brief_content: 直接传入简报文本（优先于 brief_path）

        Returns:
            命中的 proposal_id 列表；无命中则返回全部 optimizing 课题（fallback）
        """
        import re

        # 1. 获取简报内容
        if brief_content is None:
            if brief_path is None:
                brief_dir = _pl.PROJECT_ROOT / "knowledge" / "wiki" / "reviews"
                briefs = sorted(brief_dir.glob("briefing-*.md"), reverse=True)
                if not briefs:
                    if _log:
                        _log.warning("文献匹配: 未找到简报，返回全部 optimizing 课题")
                    return [p["proposal_id"] for p in self.list_by_status("optimizing")]
                brief_path = str(briefs[0])
            try:
                brief_content = Path(brief_path).read_text(encoding="utf-8")
            except Exception:
                return [p["proposal_id"] for p in self.list_by_status("optimizing")]

        # 2. 提取简报关键词（子方向 + related 标签 + 正文高频词）
        brief_keywords = set()
        # related 标签
        for m in re.finditer(r'related:\s*\[([^\]]*)\]', brief_content):
            for kw in m.group(1).split(","):
                kw = kw.strip().strip('"').strip("'").strip()
                if len(kw) > 1:
                    brief_keywords.add(kw.lower())
        # 覆盖子方向行
        for m in re.finditer(r'覆盖子方向[：:]\s*(.+)', brief_content):
            for kw in re.split(r'[、，,;；]', m.group(1)):
                kw = kw.strip()
                if len(kw) > 1:
                    brief_keywords.add(kw.lower())
        # 正文 ## 标题
        for m in re.finditer(r'^##\s+(.+)', brief_content, re.MULTILINE):
            for kw in re.split(r'[\s/]', m.group(1)):
                kw = kw.strip()
                if len(kw) > 2:
                    brief_keywords.add(kw.lower())

        if not brief_keywords:
            if _log:
                _log.info("文献匹配: 简报无关键词，返回全部 optimizing 课题")
            return [p["proposal_id"] for p in self.list_by_status("optimizing")]

        if _log:
            _log.info(f"文献匹配: 简报关键词({len(brief_keywords)}): {', '.join(list(brief_keywords)[:10])}...")

        # 3. 逐个课题匹配
        matched = []
        for prop in self.list_by_status("optimizing"):
            pid = prop["proposal_id"]
            # 读取 proposal-brief
            prop_dir = self._find_proposal_dir(pid)
            if not prop_dir:
                continue
            brief_file = prop_dir / "00_proposal-brief.md"
            if not brief_file.exists():
                continue
            try:
                prop_content = brief_file.read_text(encoding="utf-8").lower()
            except Exception:
                continue

            # 计算关键词命中数
            hits = sum(1 for kw in brief_keywords if kw in prop_content)
            hit_ratio = hits / len(brief_keywords) if brief_keywords else 0

            if hits >= 2 or hit_ratio >= 0.1:  # 至少命中2个关键词 或 10%覆盖率
                matched.append(pid)
                if _log:
                    _log.info(f"文献匹配: {pid} 命中({hits}个关键词, {hit_ratio:.0%})")

        # fallback：如果无命中，返回全部（保证不空转）
        if not matched:
            if _log:
                _log.info("文献匹配: 无课题命中今日简报，fallback 返回全部 optimizing 课题")
            return [p["proposal_id"] for p in self.list_by_status("optimizing")]

        return matched

    def run_cron_sweep(
        self,
        stagger_seconds: int = DEFAULT_STAGGER_SECONDS,
        target_proposals: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """cron 扫描：对 optimizing 区的 proposal 做每日一轮全模块对抗。

        模式（v6.6.2）：文献驱动筛选 + 每课题每天4轮（3模块各1轮+整体审查1轮）。
        不做深度连续对抗（避免触顶模型限额），每天迭代一轮即可。
        容错设计：单个 proposal 失败不影响其他 proposal。
        错峰调度：课题间留间隔，避免模型同时阻塞。

        Args:
            stagger_seconds: 课题间错峰间隔（秒）
            target_proposals: 文献匹配命中的课题ID列表；为None则全量扫描
        """
        optimizing = self.list_by_status("optimizing")
        if not optimizing:
            if _log:
                _log.info("cron 扫描: optimizing 区为空")
            return {"success": True, "swept": 0, "results": [], "empty": True}

        # 文献驱动筛选：只优化命中的课题
        if target_proposals is not None:
            optimizing = [p for p in optimizing if p["proposal_id"] in target_proposals]
            if not optimizing:
                if _log:
                    _log.info("cron 扫描: 今日无文献匹配的课题，跳过优化")
                return {"success": True, "swept": 0, "results": [], "empty": True, "reason": "无文献匹配"}

        results = []
        success_count = 0
        fail_count = 0
        advanced_count = 0

        total = len(optimizing)
        for idx, prop in enumerate(optimizing):
            pid = prop["proposal_id"]
            if _log:
                _log.info(f"cron 扫描: 每日全模块对抗 {pid} ({idx + 1}/{total})")
            try:
                # 每课题4轮：立项依据→研究内容→研究方案→整体审查
                section_results = []
                for section_idx in range(len(PROPOSAL_SECTIONS) + 1):
                    result = self.optimize_cycle(pid)
                    if result.get("success"):
                        section_results.append(result)
                    else:
                        if _log:
                            _log.warning(f"cron 扫描: {pid} 第{section_idx+1}轮失败: {result.get('error','')[:80]}")
                        break
                    # 如果中途达标，提前结束
                    if result.get("done"):
                        break

                last_result = section_results[-1] if section_results else {"success": False, "error": "所有轮次失败"}

                results.append({"proposal_id": pid, "result": last_result, "rounds_done": len(section_results)})
                if last_result.get("success"):
                    success_count += 1
                    # 达标则自动移入待校验
                    if last_result.get("done"):
                        transition = self.transition(
                            pid, "pending_review", reason=last_result.get("reason", "达标")
                        )
                        advanced_count += 1
                        if _log:
                            _log.info(f"cron 扫描: {pid} 达标 → pending_review（{len(section_results)}轮）")
            except Exception as e:
                if _log:
                    _log.error(f"cron 扫描 {pid} 失败: {e}")
                results.append({"proposal_id": pid, "error": str(e)})
                fail_count += 1
                self._record_cron_failure(pid, str(e))

            # 错峰调度：非最后一个课题时，等待间隔再处理下一个
            if idx < total - 1 and stagger_seconds > 0:
                if _log:
                    _log.info(f"cron 扫描: 错峰等待 {stagger_seconds}s 后处理下一个课题")
                _time.sleep(stagger_seconds)

        return {
            "success": fail_count < success_count,
            "swept": len(results),
            "success_count": success_count,
            "fail_count": fail_count,
            "advanced_count": advanced_count,
            "results": results,
            "empty": False,
        }

    def _record_cron_failure(self, proposal_id: str, error: str) -> None:
        """记录 cron 失败到 proposal 状态（不中断循环）。"""
        try:
            with file_lock(f"proposal-{proposal_id}"):
                prop_state = self._get_proposal_state(proposal_id)
                if prop_state:
                    failures = prop_state.get("cron_failures", [])
                    failures.append({"at": now_utc(), "error": error[:200]})
                    # 只保留最近 5 次失败记录
                    prop_state["cron_failures"] = failures[-5:]
                    prop_state["updated_at"] = now_utc()
                    self._set_proposal_state(proposal_id, prop_state)
        except Exception:
            pass

    def run_health_check(self) -> Dict[str, Any]:
        """健康检查：扫描整个生命周期系统状态，检测异常并报警。

        检查项：
        1. optimizing 区空了 → 需要新课题或人工确认初稿
        2. proposal 卡在某个状态太久 → 需要关注
        3. pending_review 有 proposal → 提醒人工核验
        4. cron 失败累积 → 需要排查
        """
        state = self._load_state()
        alerts = []
        stats = {
            "total": len(state["proposals"]),
            "by_status": {},
            "stuck_proposals": [],
            "pending_human_action": [],
        }

        for stage in LIFECYCLE_STAGES:
            count = sum(
                1 for d in state["proposals"].values() if d.get("status") == stage
            )
            stats["by_status"][stage] = count

        # 检查1：optimizing 区为空但 drafts 有 proposal → 需要人工确认
        if stats["by_status"]["optimizing"] == 0 and stats["by_status"]["drafts"] > 0:
            drafts = self.list_by_status("drafts")
            alerts.append({
                "level": "info",
                "type": "awaiting_confirmation",
                "message": f"{len(drafts)} 个初稿等待人工确认思路后进入优化",
                "proposals": [p["proposal_id"] for p in drafts],
            })

        # 检查2：整个系统完全空转（没有任何活跃 proposal）
        active_count = sum(stats["by_status"][s] for s in ["drafts", "optimizing", "pending_review"])
        if active_count == 0:
            alerts.append({
                "level": "warning",
                "type": "system_idle",
                "message": "系统完全空转：没有任何活跃 proposal。需要启动新课题或从文献简报中发现方向。",
            })

        # 检查3：pending_review 有 proposal → 提醒人工核验
        if stats["by_status"]["pending_review"] > 0:
            pending = self.list_by_status("pending_review")
            alerts.append({
                "level": "info",
                "type": "pending_review",
                "message": f"{len(pending)} 个 proposal 等待人工核验",
                "proposals": [
                    {"id": p["proposal_id"], "score": p["last_score"],
                     "rounds": p["optimization_rounds"]}
                    for p in pending
                ],
            })

        # 检查4：proposal 卡在 optimizing 超过阈值
        for pid, data in state["proposals"].items():
            if data.get("status") == "optimizing":
                updated = data.get("updated_at", "")
                cron_failures = data.get("cron_failures", [])
                if len(cron_failures) >= 3:
                    alerts.append({
                        "level": "error",
                        "type": "repeated_cron_failure",
                        "message": f"{pid} 连续失败 {len(cron_failures)} 次，需要人工排查",
                        "proposal_id": pid,
                        "last_error": cron_failures[-1].get("error", ""),
                    })

        # 检查5：v6.7.6 负反馈告警（writer-critic 进入负反馈循环）
        for pid, data in state["proposals"].items():
            if data.get("status") == "optimizing" and data.get("negative_feedback_alert"):
                reasons = data.get("negative_feedback_reasons", [])
                alerts.append({
                    "level": "error",
                    "type": "negative_feedback",
                    "message": f"{pid} 触发负反馈告警，需人工介入后清除",
                    "proposal_id": pid,
                    "reasons": reasons,
                    "local_writer_score": data.get("monitor_history", [])[-1].get("local_writer_score") if data.get("monitor_history") else None,
                    "local_critic_score": data.get("monitor_history", [])[-1].get("local_critic_score") if data.get("monitor_history") else None,
                })

        return {
            "healthy": len([a for a in alerts if a["level"] == "error"]) == 0,
            "alerts": alerts,
            "stats": stats,
            "checked_at": now_utc(),
        }

    def clear_negative_feedback(self, proposal_id: str, reason: str = "") -> Dict[str, Any]:
        """清除指定 proposal 的负反馈告警，允许链路继续运转。

        人工确认问题已修复后调用，会重置 negative_feedback_alert 并记录清除历史。
        """
        prop_state = self._get_proposal_state(proposal_id)
        if not prop_state:
            return {"success": False, "error": f"proposal 未注册: {proposal_id}"}

        if not prop_state.get("negative_feedback_alert"):
            return {"success": True, "message": "无负反馈告警需清除", "proposal_id": proposal_id}

        cleared_entry = {
            "cleared_at": now_utc(),
            "previous_reasons": prop_state.get("negative_feedback_reasons", []),
            "reason": reason,
        }
        cleared_history = prop_state.get("negative_feedback_cleared", [])
        cleared_history.append(cleared_entry)

        prop_state["negative_feedback_alert"] = False
        prop_state["negative_feedback_reasons"] = []
        prop_state["negative_feedback_cleared"] = cleared_history[-10:]
        prop_state["updated_at"] = now_utc()
        self._set_proposal_state(proposal_id, prop_state)

        if _log:
            _log.info(f"清除负反馈告警: {proposal_id} ({reason})")

        return {"success": True, "proposal_id": proposal_id, "cleared_at": cleared_entry["cleared_at"]}

    def run_daily_orchestrator(self) -> Dict[str, Any]:
        """每日编排器：一个入口执行全部 cron 任务，各环节独立、容错。

        这是系统的心跳——每天执行一次，确保持续流转。
        即使某个环节失败，其他环节照常运行。

        执行顺序：
        1. 健康检查（先发现问题）
        2. 优化扫描（处理 optimizing 区）
        3. 再次健康检查（确认结果）
        """
        if _log:
            _log.info("=== 每日编排器启动 ===")

        # 1. 初始健康检查
        health_before = self.run_health_check()

        # 2. 文献-课题匹配（v6.6.2：只优化与当天文献相关的课题）
        target_proposals = self.match_proposals_with_brief()
        if _log:
            _log.info(f"每日编排: 文献匹配命中 {len(target_proposals)} 个课题")

        # 3. 优化扫描（文献驱动）
        sweep_result = self.run_cron_sweep(target_proposals=target_proposals)

        # 4. 最终健康检查
        health_after = self.run_health_check()

        # 汇总
        summary = {
            "orchestrated_at": now_utc(),
            "health_before": {
                "healthy": health_before["healthy"],
                "alert_count": len(health_before["alerts"]),
            },
            "sweep": {
                "swept": sweep_result.get("swept", 0),
                "success": sweep_result.get("success_count", 0),
                "failed": sweep_result.get("fail_count", 0),
                "advanced": sweep_result.get("advanced_count", 0),
                "empty": sweep_result.get("empty", False),
            },
            "health_after": {
                "healthy": health_after["healthy"],
                "alert_count": len(health_after["alerts"]),
                "alerts": health_after["alerts"],
            },
        }

        if _log:
            _log.info(
                f"每日编排器完成: "
                f"扫描{sweep_result.get('swept', 0)}个 "
                f"成功{sweep_result.get('success_count', 0)} "
                f"达标{sweep_result.get('advanced_count', 0)} "
                f"告警{len(health_after['alerts'])}个"
            )

        return summary

    def setup_optimization_cron(self, schedule: str = "0 9 * * *") -> Dict[str, Any]:
        """在 pipeline-runner 上配置每日编排 cron。

        采用单一编排器入口（run_daily_orchestrator），内部分解为
        健康检查 + 优化扫描 + 结果确认，各环节独立容错。

        Args:
            schedule: cron 表达式（默认每天 09:00）

        Returns:
            {success, message}
        """
        prompt = (
            "请执行每日提案系统编排：\n\n"
            "1. 运行 `python3 scripts/proposal_lifecycle.py --daily-orchestrate`\n"
            "2. 该命令会：\n"
            "   a. 健康检查（检测异常和空转）\n"
            "   b. 深度对抗（逐个聚焦优化 optimizing 区 proposal，每个连续多轮直到达标）\n"
            "   c. 达标的自动移入待校验\n"
            "   d. 最终健康检查（确认结果和告警）\n"
            "3. 输出编排摘要\n\n"
            "执行说明：\n"
            "- 每个课题会连续执行多轮深度对抗（章节轮转+整体审查）\n"
            "- 课题间有90秒错峰间隔，避免模型阻塞\n"
            "- 整个过程可能耗时1-4小时，请耐心等待\n\n"
            "容错说明：单个 proposal 失败不影响其他 proposal。\n"
            "如果 optimizing 区为空，输出健康检查结果和告警即可。\n"
            "如果有 pending_review 的 proposal，提醒人工核验。"
        )

        env = clean_subprocess_env()

        cmd = [
            "hermes", "--profile", "pipeline-runner", "cron", "create",
            schedule, prompt,
            "--name", "每日提案系统编排",
            "--deliver", "local",
            "--workdir", str(_pl.PROJECT_ROOT),
        ]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30, env=env,
            )
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"✓ 编排 cron 已创建: {schedule}",
                    "output": result.stdout.strip()[:300],
                }
            return {"success": False, "message": f"✗ {result.stderr.strip()[:200]}"}
        except Exception as e:
            return {"success": False, "message": f"✗ {e}"}
