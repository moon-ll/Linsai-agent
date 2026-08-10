# 健康检查报告 — 2026-08-10 (04h)

**检查窗口**: 过去 4 小时（2026-08-09T~Z - 2026-08-10T~Z）
**当前版本**: v6.8.19
**测试基线**: --module 317/317 通过（含 v6.8.19 prompt 变量作用域回归 8/8）

---

## TL;DR

过去 4 小时未发现新的关键缺陷。两次提交（v6.8.18 cron 幂等修复 + v6.8.19 prompt 变量作用域修复）的代码路径在隔离环境下 317+ 测试全部通过。但有 **1 项需用户手动收尾的动作**：

| 项 | 风险 | 建议 |
|----|------|------|
| cron 重复实例仍未清理 | 中（CPU 浪费、看板抖动） | 用户手动执行一次 `--setup-cron-v2` + `--setup-monitor` 即可一次性收敛 |

---

## 1. 已修复缺陷（提交记录回顾）

### v6.8.19 — 优化循环 prompt 变量作用域（关键 bug）

**根因（已修复）**:
- `optimize.py:888` `_run_critic` 跨方法引用 `optimize_cycle` 的局部变量 `_human_feedback_block` → 每次 critic 评审必抛 `NameError`
- `optimize.py:1296` `_run_writer_optimize` 直接引用未定义变量 `section_key` → 每次 writer 优化必抛 `NameError`

**过去 4h 实际影响（看板面板统计）**:
- 4 个 critic job 失败（覆盖 4 个 proposal：general-bsv / general-order / key-transient / general-quantum）
- 5 个 writer job 失败
- 5 个 optimizing 课题全部 stuck、task_progress 卡在 0%~84%

**修复（最小化、定向）**:
- 抽出 `_load_human_feedback_block(proposal_id)` 私有方法（optimize.py:897-910）
- `_run_writer_optimize` 在调用前从 `focus_section` / `is_full_review` 派生 section_key（optimize.py:1372-1378）

**回归覆盖**:
- 新测试 `test_optimize_v6817_prompt_vars.py` 8/8 通过
- 全模块基线 317/317 通过

**置信度**: 高。修复后两条执行路径都不再依赖外部作用域变量，逻辑自洽。

### v6.8.18 — 对抗机制修复 + cron 幂等性

#### 1.1 对抗机制（高置信度修复）
- `scoring.py`: 单轮扣分上限 10 分、校准惩罚上限 4 分（解决"从 100 分被扣到 0 分"问题）
- `optimize.py`: 新增 `_load_agent_score_feedback()`，将 agent 当前分数 + 最近 3 轮评价注入 critic/writer prompt
- `agent-scores.json`: writer/critic 归零分数已重置为 60（基线对齐）
- 修复闭环完整：分数变化 → 注入 prompt → agent 看到评价 → 调整行为

#### 1.2 cron 幂等性（代码已修，但需手动收尾）
- 修复: `setup_cron_framework` / `setup_monitor` 创建前先清理同名旧实例
- **当前实测**: 32 个 cron（合理约 13）
  - `lc-daily-orchestrate`: 5 个 ⚠️
  - `lc-repair`: 5 个 ⚠️
  - `lc-prompt-optimize`: 5 个 ⚠️
  - `lc-retrospective`: 5 个 ⚠️
  - `lc-hourly-monitor`: 2 个 ⚠️
- 修复代码已写入，**但旧实例仍残留**（CHANGELOG 已注明需用户手动执行一次）

---

## 2. 关注重点排查结果

### 2.1 申请书格式完整性
- 5 个 optimizing proposal 全部存在 `04_proposal/proposal-draft.md`
- sections 拆分（v6.8.17 `sections_obj.ensure_split()`）正常工作
- v6.8.19 修复后 writer 路径不再抛 NameError，下一轮（08:30-12:30 时段）应能正常产出
- **状态**: ✓ 修复已落地，待执行验证

### 2.2 任务阻塞
- 看板 execution_history 显示: 4 critic + 5 writer 全部为 v6.8.19 已修复的 NameError
- 修复路径未引入新的失败模式（317/317 测试通过）
- **状态**: ✓ 修复已落地

### 2.3 崩溃风险路径
- 审计 `optimize.py` 全文 `_human_feedback_block` / `section_key` 引用（line 121、122、269-329、616-625、886-910、1372-1378）—— 全部正确闭合
- `sections.assemble_draft()` 在 writer 成功后调用，由 try/except 包裹（line 1390-1397），失败仅记日志不影响主路径
- `_load_human_feedback_block` 用 try/except 包裹，异常时返回空字符串（line 904-910）
- `_load_agent_score_feedback` 用 try/except 包裹，异常时返回空字符串（line 917-965）
- **状态**: ✓ 异常路径已收敛

### 2.4 知识出口
- 周末任务流水线产物缺失告警在过去 24h 重复出现（logs/linsai.log.2026-08-09 line 24-66），但都是 weekend_pipeline 内部修复逻辑正常工作（failed→pending，repair_attempt 1/3）
- 知识库 `kb-health-weekly.json` 在 cron 列表中（已有 cron 触发），无新增异常
- **状态**: ✓ 工作正常

### 2.5 资源管理
- `hermes_bridge` 子进程调用统一走 `hermes_subprocess_env`，未发现新引入的句柄泄漏
- 看板文件 `memory/system-kanban.json` 由微调度器和 lifecycle_monitor 协同写入，原子写入路径未变更
- **状态**: ✓ 无新增资源风险

### 2.6 飞书通知链路（潜在关注点）
- 日志显示多次 `lark-cli 发送失败 (exit=3): not_configured`（logs/linsai.log.2026-08-09 line 16, 35, 56...）
- **这不是 4 小时窗口内的新问题**，是历史遗留：lark-cli 未绑定到 hermes context
- 影响: 异常告警无法推送到飞书，但已记入 `monitor-alert-cache.json`，系统本身监控仍正常
- **状态**: ⚠ 已知遗留，不在本轮修复范围（需用户配置 lark-cli）

---

## 3. 其他需用户手动收尾的动作

### 3.1 清理重复 cron 实例（推荐执行一次）

```bash
python3 scripts/proposal_lifecycle.py --setup-cron-v2
python3 scripts/proposal_lifecycle.py --setup-monitor
```

执行后预期：32 → ~13 个 cron（同名 cron 各收敛为 1 个）。
后续 `lc-hourly-monitor` 不再双触发，看板时间戳稳定。

### 3.2 飞书通知配置（可选，影响告警可达性）

`lark-cli` 未绑定到 hermes context，导致异常告警无法推送到飞书。
如需启用飞书通知，按 `docs/CLAUDE-CLI-ADMIN.md` 配置 lark-cli 认证。

---

## 4. 结论

过去 4 小时未发现新的关键缺陷。
v6.8.18 + v6.8.19 的两次定向修复在隔离环境下完整通过回归测试（317/317）。
链路当前处于"修复已落地、待执行验证"状态——下个时段（08:30-12:30）的 optimize cycle 将首次使用 v6.8.19 的修复路径。

**用户操作建议（影响小、可延后）**:
1. 一次性运行 `--setup-cron-v2` + `--setup-monitor` 收敛 cron 实例
2. （可选）配置 lark-cli 以启用飞书告警