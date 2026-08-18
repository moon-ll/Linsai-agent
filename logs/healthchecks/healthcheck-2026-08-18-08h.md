# 全链路健康检查报告 — 2026-08-18 08h（北京时间）

> 范围：过去 4 小时（约 04:00-08:07 BJ）
> 结论：**未发现关键缺陷**。v6.9.24 修复运行时验证通过；设计抽查 3 项全部"正常"。

---

## 第一层：运行时健康检查

### 1.1 git 变更（过去 4 小时，2 个提交）

| 提交 | 时间 | 内容 |
|---|---|---|
| 293e32c | 04:20 | v6.9.24 审核退回清理旧轮次残留 job + test_transition_reset_jobs 14 用例 |
| 0f541e0 | 04:20 | 数据快照（bsv 54 个 r7/r8 job 归档 + 管线推进 + KB 同步产物） |

### 1.2 链路监控（lifecycle_monitor --dry-run）

- 4 个 optimizing 课题，**0 异常，0 通知**；全局 done=138 / failed=0 / pending=51 / running=1
- key-transient 96.4%｜bsv 50.0%｜order-param 54.5%｜berry 57.7%

### 1.3 cron 核查（hermes 注册表口径）

沙箱内 `crontab -l` 恒为空（环境备忘 #1），改走 hermes cron 注册表：**17 条在册**，11 类核心入口全部存在（orchestrate/daily-sync/hourly-monitor/kb-sync/kb-distill/micro-scheduler/prompt-optimize/repair/retrospective/weekend-input/output/reflection/weekend-worker）+ 4 条简报任务。微调度器 5 分钟节奏实测连续（07:45/07:50/07:55/08:00 均有启动日志）。

### 1.4 _lifecycle.json 运行态

| 检查项 | 结果 |
|---|---|
| stuck running（>1800s） | berry r1-scheme-lit_search 复查时 age=1804s 刚过阈值，属长时合法任务；下次微调度器 stale 清理（v6.8.54 设计）接管，观察项非缺陷 |
| stalled 课题（48h 无进展） | 无。最久未动为 quantum-geometry（约 13.5h，pending_review 等人属法定节点） |
| pipeline_jobs 堆积（>100） | 无。最多 83/课题（key-transient、moire） |
| failed job | 0 |

- pending_review 2 个课题等人：quantum-geometry（0.70，1 轮）、moire（0.78，8 轮）——法定人工节点，human_queue 正常承接。

### 1.5 回归测试基线

`self_test --module`：**863/863 全绿**（含 v6.9.24 新增 test_transition_reset_jobs 14/14），与基线完全一致，无新失败。

### 1.6 网关复发观察（第 10 轮，07:37 daily-reload 后）

- `check_hermes_available()`：hermes_cli=true，linsai_profile=true，gateway_status=running，banner 即时响应（0.00s）
- 网关进程存活：linsai gateway PID 16194（04:00 派发正常 + 跨日存活）
- **结论：连续 10 轮无复发，建议关闭该观察项**

---

## 第二层：代码缺陷扫描（v6.9.24 追踪）

对 `proposal_lifecycle/transitions.py` 审核退回分支的完整执行路径核查：

1. **归档依赖**：`lifecycle/utils.append_archive_jobs` 存在且实现完备——`file_lock("lifecycle-archive")` 跨进程锁 + `ARCHIVE_JOB_CAP=5000` 滚动裁剪 + `_archived_from/_archived_at` 溯源标记。
2. **dict/list 兼容**：`raw_jobs.values() if isinstance(raw_jobs, dict) else raw_jobs` 双形态取值正确。
3. **异常降级**：归档失败仅 warning 后继续清空（避免退回流程被归档故障阻塞），有日志可追溯，可接受。
4. **运行时验证**：`_lifecycle_archive.json` 实有 112 条归档 job（含 bsv 54 条）；bsv 退回后新链 26 个 job 全部 round=1、无 r7/r8 残留、无 stale derived 误调度——v6.9.24 修复目标全部达成。
5. **self_test 注册**：新套件已加入 `--module` 硬编码清单（mapping["module"] 尾部），无静默跳过。

**结论：无可信触发场景的具体缺陷，不报告。**

---

## 第三层：设计实现一致性抽查（本次 3 项）

| 机制 | 结果 | 证据 |
|---|---|---|
| #1 跨课题范例注入 | **正常（运行时实证，指针项①关闭）** | 日志 3 次实时注入：bsv content 04:20（范文 0.86 ← quantum-geometry，当前 0.73）、berry rationale 06:10（当前 0.00）、berry content 07:10（当前 0.10）；数据源为全局 `_lifecycle.json` 高分课题（≥0.70），目标均为低分课题（<0.75），方向正确 |
| #3 研究设想质量门槛 | **正常（运行时实证，指针项③关闭）** | berry r1 首个 job 为 `r1-idea_review-idea_review` 且 done（≥0.70 通过后进入优化链），符合 v6.8.26 ⑩ 前置评审设计；berry 已推进至 scheme 段（done 15/26） |
| #13/#14 链结构与 stale 治理 | **正常（轮中态）** | bsv r1 链尾顺序 full_review-writer → references-critic/writer → monitor → derived(update_vision, update_method_manual)，与 `_CHAIN_ORDER` 含 7/8 号 derived 步一致；berry lit_search 触界后将由微调度器无条件 stale 清理接管 |

附带运行时数据：#10 反馈闭环样本累积中——bsv `human_feedback_count=3`、`negative_feedback_alert=False`（静态复核已完成于 08-17，维持"待人工裁决后复验"）。

---

## 跟踪项与指针更新

| 跟踪项 | 状态 |
|---|---|
| #7 轮末终验（key-transient r4-monitor） | r4-monitor 仍 pending（score_history 尾部 0.81/0.81/0.8/0.78/0.53）；焦点轮转到位后执行，预期 references=0.53 → 不晋级且 reason≠质量收敛 |
| bsv r1 轮末 | 13/26 done；轮末验证 r2 链正常创建且无 stale derived |
| order-param r2-rationale-critic | 06:00 repair 第 2 次重试已重置为 pending（repair_attempts=2, attempts=0）；08:30 时段轮到 order-param 时执行；若再失败将触双上限（repair_attempts=3），转观察自动解锁路径 |
| berry lit_search 超时线 | age 1804s 过线，下次微调度器清理动作待观察（合法长任务被误重置则为已知设计权衡，记录不复报） |
| gateway 复发观察 | **第 10 轮通过，建议关闭** |
| 设计轮换 | 第二轮 15 项已全部核过；#10/#11 维持"待人工裁决后复验"；第三轮从 #1 重新开始（重点换运行时口径） |
| 测试基建（仅报告） | idea_review 套件 35 用例未注册 --module 静默跳过 + "自动发现"表述与硬编码清单偏差——待人工裁决 |

## 结论

过去 4 小时未发现关键缺陷。设计实现抽查：跨课题范例注入 → 正常（运行时实证）；研究设想质量门槛 → 正常（运行时实证）；微调度器链结构与 stale 治理 → 正常（轮中态）。
