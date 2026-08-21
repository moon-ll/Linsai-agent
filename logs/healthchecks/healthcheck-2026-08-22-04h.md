# 全链路健康检查报告 — 2026-08-22 04h（北京时间）

> 范围：过去 4 小时（08-22 00:01 ~ 04:02）
> 执行：LinSai-CoPilot 健康检查工具（三层诊断）
> 结论：**未发现关键缺陷**。设计抽查 #13 正常、#11 部分偏差（仅报告待裁决）。

---

## 第一层：运行时健康检查

### git 变更（过去 4h，3 个 commit，均出自 00h 健康检查会话）

| commit | 版本 | 内容 |
|--------|------|------|
| `42b2205` | v6.9.34 | 周末补跑接线测试时钟依赖修复（`orchestrator.py` +7/-2 行代码，其余为数据产物） |
| `b5c44d9` | v6.9.35 | 人工审核反馈闭环第三处断裂修复（`feedback_archive.py` +16、`optimize.py` +4、新增回归用例 56 行） |
| `158a7b4` | v6.9.35 补充 | 00h 健康检查报告与设计抽查指针更新（纯报告文件） |

### 链路健康（lifecycle_monitor --dry-run，04:01）

- 6 个课题全部 optimizing，`done=258 failed=0 pending=51 running=0`
- **异常 3 个、通知 0 条**（去重后无需新通知）：
  1. `general-berry-mnps3-rashba-20260816` 停滞：job 级最近完成 54.9h 前（>48h 且 pending=13）——00h 已触发告警，本轮为持续状态
  2. `general-quantum-geometry-inversion-20260726` 停滞：48.4h 前（**本轮新增**，周四凌晨后整个周五零时段——轮转队列尾部饥饿，见观察项 3）
  3. `kb_distill_backlog`：待蒸馏积压 376 项（阈值 300）——已知慢性问题（备忘 #7），见下方恶化数据
- `key-transient` 47.3h 逼近停滞线（pending=19，轮次仅 24%），周一观察名单
- 无 stuck running（running=0）、无 failed、无 job 堆积（单课题最多 87 < 100）

### cron 注册表（hermes linsai profile，17 条）

11 类核心条目全部在位：orchestrate / repair / hourly-monitor / micro-scheduler / prompt-optimize / retrospective / weekend-input / weekend-output / weekend-reflection / weekend-worker，另有 kb-sync / kb-distill / daily-sync 治理条目与 4 条简报。无缺失、无重复。

### 回归测试

`self_test --module`：**961/961 全量通过**（5.1s），符合基线（v6.9.34/35 后），无新增失败。

---

## 第二层：代码缺陷扫描（v6.9.34 / v6.9.35 变更路径）

### v6.9.34 — `_weekend_stage_catchup` 注入时钟

- 执行路径追踪：`now_local = now_local or datetime.now()` → `_weekend_catchup_decisions(p.state, now_local)` → job 时间戳经 `fromisoformat(...).astimezone().replace(tzinfo=None)` 统一转**本地 naive** 后与 `anchor`（naive）比较——注入值与产品路径均为 naive datetime，无 aware/naive 混比风险。
- 产品路径默认行为不变（不传参时等价旧实现）。测试注入 `datetime(2026, 8, 16, 12, 0)`（周日中午，三阶段窗口均已过）。
- **结论：无缺陷。**

### v6.9.35 — 反馈闭环 proposal_id 显式传参

- 全部调用方核对：critic 路径（`optimize.py:985`）与 writer 路径（`optimize.py:1680`）均经已修复的 `_load_human_feedback_block(proposal_id)` → `load_review_feedback_for_optimization(prop_state, proposal_id)`；生产代码无遗漏的旧式单参调用（仅 `test_feedback_injection.py` 以旧签名调用，测的正是回退兼容分支）。
- 回退分支 `proposal_id or prop_state.get("proposal_id", "")` 保留，向后兼容。
- 运行时已由 00h 检查实证（bsv 实数据返回 114 字符闭环接通）；本轮 961/961 含新增端到端用例。
- **结论：无缺陷。**

---

## 第三层：设计实现一致性抽查（第三轮，从 #11 续）

### #11 KB 健康评分 → **部分偏差（仅报告，待人工裁决）**

- **计算 ✓**：上周日反思（08-16 13:48 BJ）`reflection_kb_deep_health` 实际执行，`get_kb_health()` 产出三项指标并落盘 `knowledge/.cache/kb-health-weekly.json`：
  - 连通度 `graph_connectivity=2.35`（孤儿 0）
  - 覆盖率 `category_coverage=0.37`（222/710 页命中分类）
  - 新鲜度 `week_new=200`（周新增 growth 条目）
  - 附加：`duplicate_concepts=19`、`derived_overdue=0`
- **持久化偏差 ✗**：轮换表检查项要求"持久化到 system-kanban.json"，但看板 `kb_metrics` 仅含 `coverage_pct=5.0 / total_papers / missing_notes / trends`（`sync_engine.py` 每日 12:40 写入的**论文笔记覆盖率**口径），新鲜度与连通度两个维度不在看板中。
- **裁决点**：AGENTS.md 原文只说"每周反思时计算覆盖率/新鲜度/连通度"（已满足），未指定看板持久化；轮换表描述更严。若需看板统一展示，需在 `kb_health_weekend` 或 `sync_engine` 增写 `kb_metrics.freshness/connectivity`——涉及口径合并（category_coverage 0.37 vs coverage_pct 5.0 是两个不同指标），按规则不自动修复。
- **附带发现（观察项 7 证据强化）**：`pending_distill` 08-16 为 234 → 08-22 为 376，**6 天净增 142（约 +24/天）**，而日蒸馏配额仅 5 篇——积压加速恶化，容量缺口约 5 倍，人工裁决提速策略的紧迫性上升。

### #13 微调度器轮次优先级 → **正常**

- **静态 ✓**：`_job_priority_key`（`micro_scheduler.py:1208`）返回 `(round_num, chain_next, chain_order, scheduled_at, job_index)`，round_num 为第一维度；`_CHAIN_ORDER`（L76-88）含 `update_vision: 7`、`update_method_manual: 8`，且 `idea_review: -1` 最高优先。
- **运行时 ✓**：全量扫描 6 个课题 `pipeline_jobs`，无优先级倒置——所有 pending job 均位于各自课题当前最高轮（r1/r2/r4/r7），不存在"高轮已 done 而低轮仍 pending"的抢占错序。
- **回归 ✓**：`test_derived_job_priority.py`、`test_idea_review.py`（优先级 -1 断言）在 961 套件内通过。

---

## 处置记录

- 确认 Bug：0（无需修复）
- 设计偏差报告：1（#11 看板持久化口径，待人工裁决）
- 报告与指针已静默保存并提交 git（`v6.9.35 补充 - 04h 健康检查报告与设计抽查指针更新`）

## 观察项（滚动更新至指针）

1. **周一轮转恢复观察（升级）**：berry（54.9h）、quantum-geometry（48.4h，本轮新增停滞）、key-transient（47.3h，逼近线）三个队列尾部课题——周一 00:30 时段恢复后应陆续获得时段；若周一晚仍零推进，升级排查轮转队列调度（4 时段/日 vs 6 课题的结构性饥饿）。
2. **反馈闭环生效观察（v6.9.35 修复后）**：bsv 下轮优化 critic/writer prompt 应实际注入第 3 次反馈内容，最早周一 00:30 时段可观察。
3. **kb 蒸馏积压恶化**：234→376（+142/6 天），加速恶化中——需人工裁决提速策略（提高每日配额 / 周末批量蒸馏 / 降低入池速率）。
4. 周六 09:00 周末输入端将首次在 v6.9.34 补跑修复后运行（本周窗口内无超期场景，属常规路径）。
