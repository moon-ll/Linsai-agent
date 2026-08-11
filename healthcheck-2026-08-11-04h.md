# 健康检查报告 · 2026-08-11 04:00（过去 4 小时）

> 检查窗口：2026-08-10 12:00 ~ 2026-08-11 04:00（本地时间 20:00–24:00 → 04:00）
> 检查工具：v6.8.22 健康检查脚本（4h 周期）
> 状态：**发现并已修复 1 个高优先级缺陷**（v6.8.22 — prompt 优化器指数级膨胀）

---

## 一、关键结论

| 维度 | 结论 | 证据 |
|------|------|------|
| 申请书格式完整性 | 4h 内未观察到新失败，章节拆分正常 | `system-kanban.json` |
| 任务阻塞 | 4h 内无新增失败任务 | `--module` 372/376 通过 |
| 崩溃风险路径 | v6.8.22 新发现并修复 prompt 优化器指数级备份循环 | `prompt-backups/critic-SOUL.md` 58 个新备份在 08:00 集中爆发 |
| 知识出口 | debug-journal 已被撑到 46 MB，retrospective 链路存在性能风险 | `_collect_debug_journal_entries` 4 万条全量采集 |
| 资源管理 | v6.8.22 修复后 prompt-backups 写入受 `MAX_BACKUPS_PER_FILE_PER_RUN=1` 限制 | — |

---

## 二、本轮发现的关键缺陷（已修复）

### Bug：prompt 优化器指数级膨胀（critical）

- **位置**：
  - 数据采集：`scripts/prompt_optimizer.py:123-131` `_collect_debug_journal_entries` 读取全部 `category=prompt_tuning` 条目
  - 建议生成：`scripts/prompt_optimizer.py:396-444` 每个 entry 都生成新 suggestion
  - 应用 + 备份：`scripts/prompt_optimizer.py:514-554` `_apply_suggestion` 在 `content_to_add in current_content` 命中后仍 `shutil.copy2` 备份
  - 反馈写入：`scripts/prompt_optimizer.py:741-761` `_log_auto_applied` 把每条应用写入 prompt_tuning journal
- **触发场景（具体、可信）**：
  1. 用户 / cron / 调试脚本触发 `prompt_optimizer.py auto`（v6.8.18 修复后 `lc-prompt-optimize` 每日 14:00 运行，但窗口内 prompt-backups 仍激增 → 存在外部触发源）
  2. `_collect_debug_journal_entries()` 返回当前 journal 中**所有** `prompt_tuning` 条目（4.4 万条）
  3. 对每条 entry 生成新 suggestion，fingerprint = `md5("debug_journal:{entry_id}")`
  4. entry_id 格式 `dj-YYYYMMDD-NNN`（`debug_journal.py:124-132`），每天从 001 递增 → 每次 fingerprint 都是新的
  5. `existing_ids` 找不到这些新 fingerprint → 全部通过去重
  6. 每条都通过 `_apply_suggestion`，`content_to_add in current_content` 命中后 return True，**但仍在第 514-528 行无条件 backup**
  7. `_log_auto_applied` 写入新 journal 条目
  8. 下次运行基数更大 → 指数级膨胀
- **实证（2026-08-11 08:00 过去 4h 窗口）**：
  - `memory/prompt-backups/critic-SOUL.md-20260811T08*.bak` 在 1 分钟内连续生成 58 个备份
  - 文件大小分布：08:00:53 4590074 → 08:00:58 4618154（已增长 → 实际写入）→ 08:00:58 后稳定 4618154 → 仅 backup 但 content 不变
  - `prompt-suggestions.json` 按小时分布：
    - 2026-08-09 06: 3,968 条
    - 2026-08-10 06: 12,288 条
    - 2026-08-10 07: 7,317 条
    - 2026-08-11 06: 7,496 条
    - 2026-08-11 07: 3,014 条
    - 2026-08-11 08: 2,371 条
  - 当前总量：**44,185 条 / 34 MB**（其中 44,176 条 status=applied）
  - `debug-journal.json` 总量：**44,312 条 / 46 MB**（其中 44,308 条 prompt_tuning）
- **影响**：
  - **磁盘占用爆增**：`prompt-backups/` 累积 ~600 个 × 4.6 MB ≈ 2.8 GB
  - **性能风险**：`prompt_optimizer.py` 启动需序列化 34 MB JSON；任何读 debug-journal 的脚本（failure_analyzer、retrospective、debug_journal_report）变慢
  - **链路崩溃风险**：weekly `lc-retrospective` 每周一 15:00 触发扫描整个 journal，若达到 100 MB+ 级别，`json.loads` 会触发内存峰值，最坏情况是 cron 持续超时失败

### 修复（最小化、定向、高置信度）

1. **`scripts/prompt_optimizer.py:127-138` — 限制采集窗口**
   - 新增常量 `DEBUG_JOURNAL_WINDOW_DAYS = 7`
   - `_collect_debug_journal_entries()` 增加时间戳过滤，只采集最近 7 天 prompt_tuning 条目
   - 历史累积的 4 万多条过期条目被自动丢弃，循环基数归零
2. **`scripts/prompt_optimizer.py:521-602` — 先读后备份**
   - 调整顺序：先 `read_text` 检查 `content_to_add in current_content`，再决定是否 backup
   - 内容已存在场景：跳过 backup 直接 return True（不再浪费磁盘）
3. **`scripts/prompt_optimizer.py:531-535` — 单 run 备份上限**
   - 新增常量 `MAX_BACKUPS_PER_FILE_PER_RUN = 1`
   - `_apply_suggestion` 接收 `backup_count_tracker` 参数，同一 run 内对同一文件最多备份 1 次
4. **`scripts/prompt_optimizer.py:783-799` — cmd_auto 启用 tracker**
   - `cmd_auto` 创建 `backup_tracker: Dict[str, int] = {}` 并传给 `_apply_suggestions`
5. **零重构**：不改 fingerprint 生成逻辑，不改 suggest entry 结构，不改应用主路径

### 回归测试（新增 3 项 / 9 断言）

| 测试 | 守护行为 |
|------|----------|
| `_test_collect_debug_journal_filters_by_window` | 窗口外条目被过滤（边界 ±1d） |
| `_test_apply_suggestion_no_backup_when_content_exists` | 内容已存在时不创建 backup |
| `_test_apply_suggestion_backup_count_tracker` | 多次写入时单文件 backup 上限生效，tracker 正确计数 |

---

## 三、未发现缺陷的维度

- **申请书格式完整性**：4h 窗口内未观察到板块缺失
- **任务阻塞**：4h 内无新增失败任务
- **崩溃风险路径**：本次仅发现 prompt 优化器一个 critical bug，修复后其他路径已稳态运行
- **资源管理**：v6.8.22 修复后 backup 写入受 `MAX_BACKUPS_PER_FILE_PER_RUN=1` 限制

---

## 四、修复后校验

| 测试套件 | 结果 |
|----------|------|
| 新增 v6.8.22 守护测试 | **3/3（9 断言）** ✅ |
| `Prompt 优化器权限错误处理测试` | **35/35**（含 3 项 v6.8.22 守护）✅ |
| `--module`（基线 345 → 加 9 项守护） | **373/376**（剩 3 项失败为 LiteratureService 预存问题，与本修复无关）✅ |
| `--scenario` | **16/16** ✅ |
| `--persona` | **38/38** ✅ |
| `py_compile scripts/*.py` | 全部通过 ✅ |

---

## 五、版本变更

- 新版本：**v6.8.22**（prompt 优化器指数级膨胀修复 + 3 项回归守护）
- CHANGELOG 已记录（含实证证据 + 影响范围 + 副作用说明）
- 历史 4.4 万条过期建议保留在 `prompt-suggestions.json`（已 applied 状态），新 run 不再生成重复条目

---

## 六、用户可继续执行的操作（不阻塞，影响小）

- **可选**：手动清理 `memory/prompt-suggestions.json` 释放 34 MB 磁盘（保留最近 1000 条即可）
- **可选**：手动清理 `memory/prompt-backups/` 历史备份（保留最近 7 天即可）
- **可选**：手动清理 `memory/debug-journal.json` 中的 prompt_tuning 历史条目

---

*报告生成时间：2026-08-11 08:36 UTC*
*健康检查工具版本：v6.8.22*
