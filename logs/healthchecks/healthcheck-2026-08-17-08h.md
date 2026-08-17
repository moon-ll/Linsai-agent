# 全链路健康检查报告 — 2026-08-17 08h（北京时间）

执行时间：08:01–08:21 BJ ｜ 工具：三层诊断（运行时 / 代码扫描 / 设计一致性）

## 执行摘要

**P0 演进：gateway 已于 07:37 重启，但 linsai profile 派发层仍然死亡——且本次拿到决定性新证据：新网关进程在启动早期即挂死（阻塞在模块导入链的 `open()` 系统调用上），属可复现的启动挂死，非运行态冻结。** 昨日 30485 与今日 3538 两个替换进程呈现完全相同的挂死模式，而同刻重启的默认 profile 网关（3535）运转正常。首次观察到"根目录 ticker 在跳"的假恢复信号，环境备忘已修正 ticker 判读口径。CoPilot 侧代码零缺陷（4h 零代码变更，self_test 840/840 全绿）；设计抽查 3 项全部正常。

---

## 第一层：运行时健康检查

### 1. git 变更（4h 窗口）

- 唯一 commit `b06da3b`（04:11）仅含上轮指针 + 报告文件，**零代码变更** → 第二层扫描无对象。
- 未提交变更均为 `knowledge/` 数据文件（08-16 22:40 手动蒸馏批次产物），随 395 未跟踪数据入库策略待人工（累积项不变）。

### 2. 链路健康（lifecycle_monitor --dry-run）

- 5 个 optimizing 课题，7–8 个异常，dry-run 零通知；看板 done=245 failed=2 pending=55 running=0。
- **告警防线无失明**（手动运行口径）；stalled×2 / cron_stale 等检出逻辑上轮已实证，本轮异常计数构成一致。
- 复现既知工具副作用：2 分钟内连跑两次 dry-run，异常 8→7（zero_progress 因 prev_ts 刷新提前 resolve），与 04h 备忘吻合——**读数以单次运行为准**。

### 3. cron 注册表（沙箱 crontab 假阴性，以 hermes 注册表为准）

- 13 条 lc- 全部在位且 enabled=true；`validate_cron_topology()` 对账 **零缺失/重复/漂移**（schedule 全一致）。
- 关键陈旧度：`lc-hourly-monitor` last_run=08-16 07:00（**今日 08:00 已错过**，next_run_at 冻结在 08-16T08:00）；`lc-micro-scheduler` completed=0 从未执行；`lc-repair` last_run=08-16 06:00（今日 06:00 错过）。
- pipeline-runner 网关（PID 70614，07-26 起）健康存活，与本案无关。

### 4. 课题状态（`research_proposals/_lifecycle.json`）

- 无 stuck running job（running=0）。
- 2 个 failed 双上限终态 job（详见设计抽查①）：moire r8-full_review-writer、order-param r1-references-critic，均满足自动解锁条件，等待 repair 派发。
- pipeline_jobs 最多 83 个（<100 阈值）；课题年龄 28–56h（停摆叠加周末预期）。
- berry（drafts）等人工激活 20.2h，催办线 08-19 11:49 BJ 不变。

### 5. 回归测试

- `self_test --module`：**840/840 全绿**（3.565s），基线维持。

---

## P0 专题：gateway 第 7 轮跟踪 — 重启已发生，挂死换了形态

### 时间线（全部实证）

| 时刻（BJ） | 事件 |
|---|---|
| 08-16 07:37:00 | 旧 linsai 网关收 SIGTERM（daily-reload launchd bootout），07:37:03 exit 1 |
| 08-16 07:37:15 | 替换进程 PID 30485 被 bootstrap 启动 → **启动挂死**（昨日第 6 轮跟踪对象） |
| 08-17 07:37:04 | daily-reload 再次 bootout（30485 被杀，本轮 ps 确认已消失） |
| 08-17 07:37:15 | 新进程 PID 3538 启动（launchd，XPC `ai.hermes.gateway-linsai`） |
| 08-17 07:37–08:03 | 3538 存活 26 分钟：CPU 仅 0:00.15，**gateway.log 零写入**（mtime 停在 08-16 07:37，fd 停在 EOF），未派生 MCP watchdog 子进程 |
| 08-17 08:00 | `lc-hourly-monitor` 未派发（注册表 last_run 无更新）→ 派发层死亡实锤 |

### 决定性新证据：启动挂死定位（`sample 3538`）

主线程 100% 采样阻塞于：

```
main → pymain_run_module → exec(hermes_cli.main) → PyImport_ImportModuleLevelObject
     → exec(被导入模块) → PyImport_ImportModuleLevelObject → _io_open → open()  ← 阻塞
```

- 物理内存仅 22MB、无网络 fd、无锁 fd → **卡在解释器启动后第二次模块导入的文件打开上**，远未到达网关横幅/MCP/调度器初始化。
- `open()` 对普通文件不阻塞；阻塞场景为 FIFO/特殊设备/停滞文件系统。profile 目录及 `~/.hermes` 顶层未发现 FIFO（`find -type p` 空）→ 阻塞目标疑在更深层路径或特殊文件，需 hermes-agent 侧排查。

### 假恢复信号澄清（重要，已更新环境备忘）

- `~/.hermes/cron/ticker_heartbeat`（**根目录**）08:02 仍在刷新——属**默认 profile 网关 PID 3535**（`HERMES_HOME=~/.hermes`，`ai.hermes.gateway`，同刻重启后健康：CPU 8.97s、日志流动、持有 kanban dispatcher 锁）。
- **linsai profile 的 ticker**（`~/.hermes/profiles/linsai/cron/ticker_heartbeat`）仍冻结在 08-16 07:36，jobs.json 冻结在 08-16 07:20。
- 结论：判读恢复必须用 profile 路径 ticker + profile gateway.log 新增行，根目录 ticker 与 linsai 无关。

### 根因线索（推断，待人工确认）

- daily-reload 日志证实每日 07:37 launchd bootout/bootstrap 双 profile 网关；08-15 07:37 那次 linsai 网关正常完成启动（有横幅），**08-16/08-17 两次替换均挂死**。
- hermes-agent 运行时 generation-1786761045 创建于 **08-15 10:31**（epoch 换算），且 08-15 13:47 存活网关报 `ImportError: INDICATOR_STYLES`（commands.py 顶层导入）——指示 08-15 白天 hermes-agent 发生过代码/运行时更新。
- 默认 profile 网关用同一运行时正常 → 挂死条件与 `HERMES_HOME=profiles/linsai` 的状态/环境相关。
- 处置边界：本工具未做任何进程操作（kill/重启探针已按用户接管取消）；进程级修复移交人工。

### 若修复恢复，自愈清单（按时间顺序）

1. repair 派发（下一次 12:00）→ 2 个双上限 job 自动解锁重跑（条件已全部满足，见抽查①）
2. 整点监控恢复 → cron_stale/stalled 告警随真实心跳自愈
3. 08:30–12:30 worker 时段 → #1 范例注入实测窗口（order-param writer ← bsv 范文）
4. 12:40/12:50 KB 治理（当前停更将满 3 个周期）
5. key-transient r4 轮末 _check_done 终验（reason="质量收敛"）

---

## 第二层：代码缺陷扫描

**无对象**：4h 窗口唯一 commit 仅日志文件，零代码变更。未提交 knowledge/ 为数据产物，无执行路径可追踪。

---

## 第三层：设计实现一致性抽查（本轮 3 项）

### ① 双上限终态自动解锁（辅助链路·定期修复 v6.8.54）— 正常

- 代码链完整：`should_auto_unlock`（`lifecycle/utils.py:78`，5 条件：failed + attempts≥MAX + repair_attempts≥MAX + auto_unlock_count<1 + finished 超 24h，异常兜底 False）；解锁执行（`lifecycle/orchestrator.py:398-424`：置 pending、attempts 归零、error_history 记录"自动解锁(v6.8.54)"）。
- 运行时实证：moire r8-writer（attempts=3, repair_attempts=4, finished 57.7h 前）、order-param r1-critic（3/3, 59.7h 前）**均满足全部条件**，repair 一旦派发即解锁。
- 附注（仅记录）：moire repair_attempts=4 超上限 1 次，超出 repair 路径理论最大值 3，属历史遗留增量（旧版本或并行写入），不影响 ≥3 终态判定语义。

### ② cron 拓扑对账（辅助链路·健康检查，cron_manifest 单一真相源）— 正常

- `validate_cron_topology(actual)` 返回 `[]`：8 固定 + weekend/KB 扩展共 13 条 lc- 与清单零缺失、零重复、零 schedule 漂移。
- 该防线在网关死亡期间持续可用（纯文件对账，不依赖派发）。

### ③ 告警缓存与 dry-run 口径（辅助链路·健康检查）— 部分观察（维持既知备忘，不修复）

- dry-run 实际仍合并写看板（"看板已更新"日志），"dry-run 零落盘"指告警/通知不落盘，看板除外——两次手动运行 2 分钟间隔即触发 zero_progress 提前 resolve（本轮 8→7 异常复现）。
- 告警缓存最后真实落盘 08-16 12:01（此后零派发，与挂死时间线吻合）。
- 生产影响：无（真实派发路径为 cron，间隔 1h 不会触发该副作用）；建议健康检查工具单次读数。

---

## 结论与移交

- **CoPilot 代码侧本轮零缺陷、零修复**（报告类提交，沿用 v6.9.20 标注）。
- **P0 移交人工（第 7 轮，证据升级）**：linsai 网关启动挂死，sample 已定位到导入链 `open()` 阻塞；建议人工路径：a) 前台运行 `hermes --profile linsai gateway run` 复现并观察卡点文件；b) 检查 hermes-agent 08-15 更新引入的导入期文件打开（FIFO/特殊路径）；c) 必要时回滚 runtime generation-1786761045；d) 修复后验证 profile ticker + gateway.log 横幅 + 12:00 repair 解锁 2 job。
- 待人工决策清单（累积，无变化）：gateway 启动挂死处置（P0，证据升级）/ berry 激活 / #11 kb_health 三选一 / #10 反馈闭环三选一 / #2 维度轮换死代码裁决 / 46 占位名改名 / 395+手动批次数据入库策略 / 飞书 config init 或 config bind --source hermes。

## 下轮从这里继续

- gateway 第 8 轮：若人工已处置 → 验证 profile ticker 恢复、gateway.log 新增横幅、12:00 repair 派发与 2 job 解锁（auto_unlock_count 应=1）；若未处置 → 12:40/12:50 KB 治理将连续第 3 日缺失、worker 时段第二次空转，继续记录
- #1 范例注入实测窗口（若恢复）：order-param writer 首次调用应注入 bsv 范文段
- key-transient r4 轮末终验（若恢复且 worker 推进）
- berry 激活跟踪：催办线 08-19 11:49 BJ
- 设计轮换：从 #9 输入端熔断（四复核）起继续，或按恢复态势优先 #7 终验
