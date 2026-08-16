# 全链路健康检查报告 — 2026-08-17 04h（北京时间）

- 执行时间：2026-08-17 04:01–04:09 BJ（Asia/Shanghai）
- 范围：过去 4 小时（00:00–04:00）三层诊断
- 上轮报告：healthcheck-2026-08-17-00h.md

## 结论速览

**未发现新增关键缺陷。** P0 gateway 挂死进入第 6 轮（未解除，等人工重启）。回归基线 840/840 全绿，过去 4 小时零代码提交（唯一 commit 仅指针文件）。

设计实现抽查：
- #8 停滞课题检测 → 正常（运行时实证：2 条真阳性 stalled）
- 辅助链路·cron 陈旧防线 → 正常（实时双标记；周末延迟特性属设计行为）

## 第一层：运行时健康检查

### 1. git 变更

```
c5bd887 v6.9.20 - 健康检查 00h：gateway 挂死第5轮未解除…（仅 logs/healthchecks/design-check-pointer.txt，+15/-5）
```

过去 4 小时**无任何代码变更**，第二层缺陷扫描无可追踪对象。

### 2. lifecycle_monitor --dry-run

5 课题、5 个活跃告警（通知 0 条属 dry-run 设计）。活跃告警构成：

| 告警 | 级别 | 内容 | 判定 |
|------|------|------|------|
| cron_stale | medium | lc-repair 长时间未执行（首触发 08-16 18:51 BJ） | 真阳性：gateway 挂死 |
| stalled ×2 | medium | quantum-geometry（25/30，5 pending）、key-transient（66/79，13 pending）停滞 48h，first_seen 00:03 BJ | 真阳性：gateway 挂死（00h 预测的周一告警波兑现） |
| stuck ×2 | medium | moire r8-full_review-writer（att=3/ra=4）、order-param r1-references-critic（att=3/ra=3）超时 | 已知双上限终态，等 repair 自动解锁 |

实时调用 `_check_cron_status()` 确认当前判定：`lc-micro-scheduler (从未执行); lc-repair (22h 未执行)` 双标记。

### 3. cron 注册表与 ticker

- 注册表（~/.hermes/profiles/linsai/cron/jobs.json）：13 条 lc- 条目全部 enabled=True、paused=False，无缺失/重复/漂移（拓扑对账通过）。
- ticker_heartbeat / ticker_last_success / .tick.lock / executions.db 全部冻结在 **08-16 07:20–07:36**。
- 沙箱 `crontab -l` 假阴性（已知环境备忘），以注册表 + ticker 为准。

### 4. research_proposals/_lifecycle.json

- 6 课题（5 optimizing + 1 drafts[berry]）；running=0，无 stuck running（>1800s）。
- job 堆积最大 83（moire），均 <100 阈值。
- 2 个双上限 failed job 均满足自动解锁条件（attempts≥3 ∧ repair_attempts≥3 ∧ finished>24h ∧ auto_unlock_count=0），解锁窗口顺延至**今日 06:00 repair**（若 gateway 恢复）。

### 5. self_test --module

**840/840 全量通过**（总耗时 3.6s），无新增失败。

## P0 gateway 挂死 — 第 6 轮跟踪

| 指标 | 数值 | 对比 00h |
|------|------|---------|
| PID 30485 | 存活，elapsed 20:24:41 | 持续存活 |
| 累计 CPU | 0:00.23 | +0.01s（冻结确认） |
| ticker 冻结点 | 08-16 07:36:50 | 无变化 |

- **周一 00:30–03:30 worker 时段空转确认**：00:05→04:01 日志零派发活动，running=0，done=245 持续 21h 无变化（00:03–00:05 的 monitor/记忆活动为上轮健康检查手动运行痕迹）。
- 01/02/03/04 整点监控全缺（04:01/04:03 为本工具手动运行，不计入 cron last_run）。
- 影响面（若持续）：06:00 repair 再缺 → 2 stuck job 解锁继续顺延；08:55 起 orchestrate 43.2h→48h 触发 cron_stale 第三条目；今日 12:40/12:50 KB 治理将连续第 2 日缺失（kb_metrics 已停更 39.4h）。
- 防线表现：cron_stale（repair 线，首触发延迟 11.25h）+ stalled ×2 + zero_progress（21h 停滞，04:01 触发）均正确产出——**告警层无失明**，失明的是派发层本身。
- 本工具不干预进程（00h kill 已被用户接管），维持移交人工。

## 第二层：代码缺陷扫描

过去 4 小时无代码变更，无新增缺陷。两项观察（不构成 Bug，均有可信解释）：

1. **看板告警 message 为首次触发快照**：去重语义下仅 count/last_seen 刷新（lifecycle_monitor.py:678-679），message 保留首次文本——cron_stale 显示"12h 未执行"实际已 22h。人工读板应以 last_seen 为准。可观测性瑕疵，未达修复门槛。
2. **手动 2 分钟内连跑两次 monitor 会提前 resolve zero_progress**：第二次运行将 prev_ts 刷新至 2 分钟前，stale_hours 归零（<3h 阈值）。本工具自身行为副作用，生产小时节奏不受影响；记录以免下轮误读 6→5 异常数波动。

## 第三层：设计实现一致性验证（本轮 2 项）

### #8 停滞课题检测 → 正常（运行时实证）

- 代码在位：lifecycle_monitor.py:285-307，48h 窗口 + pending>0 口径（08-15 已修复口径，本轮零漂移）。
- 运行时兑现：quantum-geometry / key-transient 于周一 00:03 BJ 首次触发（first_seen 2026-08-16T16:03:45Z），与 08-16 08h 轮"预测周一 00:00–08:00 告警波"完全吻合；消息含 done/pending 计数与处置建议文案。
- 根因归因：gateway 真死亡（ticker 冻结 + 零派发），非周末宽限误报——上轮悬置的"是否加周末宽限"议题在本案不适用（死亡跨越工作日）。

### 辅助链路·cron 陈旧防线（健康检查链路）→ 正常（含设计特性观察）

- 检测范围：仅 3 条关键 cron（micro-scheduler / daily-orchestrate / repair），调度感知阈值 max(2h, interval×2)。
- 实时验证：`_check_cron_status()` 返回 micro-scheduler（从未执行，created_at 在位非死代码）+ repair（22h）。
- **设计特性**：v6.9.2 星期域感知使 `*/5 * * * 1-5` 的 micro-scheduler 周末免检——周日 07:36 冻结场景下，最快检出线是 repair 的 12h 阈值（实际 18:51 BJ 触发，延迟 11.25h）。属周末宽限与检出速度的固有权衡，非缺陷；若需更快检出可考虑把 hourly-monitor（阈值 2h）纳入陈旧检测范围（仅报告，不动代码）。
- 附注：gateway ticker 冻结本身无专用告警，cron_stale 为间接代理；hermes_bridge.list_team_profiles 的 heartbeat_alive（5 分钟新鲜度）供 Web 控制台展示，当前应为 False——控制台侧可见性存在。

### 跟踪项（非本轮正式抽查）

- **key-transient r4 轮末终验**：悬置（worker 未推进，13 pending；_check_done 未执行，恢复后自裁决）。
- **berry 激活**：drafts 等 16.2h（起点 08-16 11:49 BJ）。**时间线修正**：human_queue.py:40 `ESCALATE_AFTER_H=72.0`，催办线应为 **08-19 11:49 BJ**（上轮指针"08-17 11:49"疑为 24h/72h 混淆）。#3 运行时实测继续被此人工节点阻塞。
- **#1–#7/#9–#15 全部机制**：4h 零代码提交，静态零漂移；运行时实证均被 P0 阻塞。
- **12:40/12:50 KB 治理回查**：kb_metrics 停更 39.4h（错过 08-16 一日周期），今日 12:40 若 gateway 恢复将刷新；agent-scores 停更 58.2h（周末无 meta-review + 挂死叠加，符合预期）。蒸馏积压告警未复燃（v6.9.20 手动批次清零后 health_signals 保持 resolved）。

## 待人工决策清单（滚动更新）

1. **gateway 重启（P0，第 6 轮）**：`hermes --profile linsai gateway run --replace` 或 kill 30485 后重启；恢复后自愈项——ticker 恢复 / 06:00+ repair 解锁 2 stuck job / 整点监控 / 今日 12:40 KB 治理
2. berry 激活（drafts 等 16.2h，催办线 08-19 11:49 BJ）
3. #11 kb_health 三选一（周频指标入 kanban 与否）
4. #10 审核反馈闭环三选一（守卫放宽 / 全入口带 session / 接受现状）
5. #2 对抗维度轮换死代码裁决
6. 46 个占位名改名 / 395+ 手动批次数据文件入库策略
7. 飞书 config init 或 config bind --source hermes（通知链路恢复）
8. （新增，低优先）是否将 lc-hourly-monitor 纳入 cron 陈旧检测范围以缩短周末检出延迟

## 下轮从这里继续

- gateway 第 7 轮：06:00 repair 派发与否（2 stuck job 解锁判定点）；08:55 orchestrate 48h 线
- 12:40/12:50 KB 治理回查（若恢复：kb_metrics/蒸馏刷新确认）
- key-transient r4 轮末终验 / berry / #1 实测窗口（均被 P0 阻塞，恢复后逐一解锁）
